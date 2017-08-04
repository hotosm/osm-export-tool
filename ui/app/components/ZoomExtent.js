import detectIt from "detect-it";
import Control from "ol/control/control";
import ol from "ol";

const ZoomExtent = function(options) {
  options = options || {};
  options.className = options.className != null ? options.className : "";

  let button = document.createElement("button");
  button.setAttribute("type", "button");
  let icon = document.createElement("i");
  icon.className = "fa fa-globe";
  button.appendChild(icon);

  this.zoomer = () => {
    const map = this.getMap();
    const view = map.getView();
    const size = map.getSize();
    view.fit(options.extent, size);
  };

  button.addEventListener("click", this.zoomer, false);
  button.addEventListener(
    "touchstart",
    this.zoomer,
    detectIt.passiveEvents ? { passive: true } : false
  );
  let element = document.createElement("div");
  element.className = options.className + " ol-unselectable ol-control";
  element.appendChild(button);

  Control.call(this, {
    element: element,
    target: options.target
  });
};

ol.inherits(ZoomExtent, Control);

export default ZoomExtent;
