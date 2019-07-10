Use this command to get your azure CLIENT_ID and CLIENT_SECRET for [Packer](https://www.packer.io/docs/builders/azure-setup.html):

```
az ad sp create-for-rbac -n "Packer" --role contributor --scopes /subscriptions/<SUBSCRIPTION_ID>
```