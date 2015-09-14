import logging
from social import utils
from social.exceptions import InvalidEmail

from django.core import signing
from django.core.signing import BadSignature
from django.contrib.sessions.models import Session
from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core import signing
from django.core.mail import EmailMultiAlternatives

from social.pipeline.partial import partial

logger = logging.getLogger(__name__)

@partial
def require_email(strategy, request, details, user=None, is_new=False, *args, **kwargs): # pragma: no cover
    logger.debug(user)
    if kwargs.get('ajax') or user and user.email:
        return
    elif not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return redirect('require_email')
    """
    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
            logger.debug(email)
        else:
            return redirect('require_email')
    """

def email_validation(strategy, backend, code): # pragma: no cover
    """
    Send an email with an embedded verification code and the necessary details to restore the required session
    elements to complete the verification and sign-in, regardless of what browser the user completes the
    verification from.
    """
    signature = signing.dumps({"session_key": strategy.session.session_key, "email": code.email},
                              key=settings.SECRET_KEY)
    verifyURL = "{0}?verification_code={1}&signature={2}".format(
        reverse('osm:complete', args=(backend.name,)),
        code.code, signature)
    verifyURL = strategy.request.build_absolute_uri(verifyURL)   
 
    emailText = ''
    emailHTML = """Welcome to MyApp!
    In order to login with your new user account, you need to verify your email address with us.
    Please copy and paste the following into your browser's url bar: {verifyURL}
    """.format(verifyURL=verifyURL)
 
    logger.debug(code.email)
    kwargs = {
        "subject": "Please Verify Your Account",
        "body": emailText,
        "from_email": "HOT Exports <exports@hotosm.org>",
        "to": [code.email]
    }
    
    email = EmailMultiAlternatives(**kwargs)
    email.attach_alternative(emailHTML, "text/html")
    email.send()
    


def partial_pipeline_data(backend, user=None, *args, **kwargs): # pragma: no cover
    """
    Monkey-patch utils.partial_pipeline_data to enable us to retrieve session data by signature key in request.
    This is necessary to allow users to follow a link in an email to validate their account from a different
    browser than the one they were using to sign up for the account, or after they've closed/re-opened said
    browser and potentially flushed their cookies. By adding the session key to a signed base64 encoded signature
    on the email request, we can retrieve the necessary details from our Django session table.
    We fetch only the needed details to complete the pipeline authorization process from the session, to prevent
    nefarious use.
    """
    data = backend.strategy.request_data()
    if 'signature' in data:
        try:
            signed_details = signing.loads(data['signature'], key=settings.SECRET_KEY)
            session = Session.objects.get(pk=signed_details['session_key'])
        except BadSignature, Session.DoesNotExist:
            raise InvalidEmail(backend)

        session_details = session.get_decoded()
        backend.strategy.session_set('email_validation_address', session_details['email_validation_address'])
        backend.strategy.session_set('next', session_details.get('next'))
        backend.strategy.session_set('partial_pipeline', session_details['partial_pipeline'])
        backend.strategy.session_set(backend.name + '_state', session_details.get(backend.name + '_state'))
        backend.strategy.session_set(backend.name + 'unauthorized_token_name',
                                     session_details.get(backend.name + 'unauthorized_token_name'))

    partial = backend.strategy.session_get('partial_pipeline', None)
    if partial:
        idx, backend_name, xargs, xkwargs = \
            backend.strategy.partial_from_session(partial)
        if backend_name == backend.name:
            kwargs.setdefault('pipeline_index', idx)
            if user:  # don't update user if it's None
                kwargs.setdefault('user', user)
            kwargs.setdefault('request', backend.strategy.request_data())
            xkwargs.update(kwargs)
            return xargs, xkwargs
        else:
            backend.strategy.clean_partial_pipeline()
            
utils.partial_pipeline_data = partial_pipeline_data
