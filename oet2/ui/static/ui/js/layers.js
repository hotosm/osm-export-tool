/*
 * Configuration for base layers.
 */
var Layers = {};

// Layers.OSM = new OpenLayers.Layer.OSM("OpenStreetMap");
Layers.OSM = new ol.layer.Tile({
	title: "OpenStreetMap",
	source: new ol.source.OSM()
});

// Layers.HOT = new OpenLayers.Layer.XYZ("Humanitarian OSM",
//                 ["//a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
//                  "//b.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
//                  "//c.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
//                 ],
//                 {
//                     isBaseLayer: true,
//                     sphericalMercator: true,
//                 }
//             );
Layers.HOT = new ol.layer.Tile({
	title: "Humanitarian OSM",
	source: new ol.source.XYZ({
		url: "//{a-c}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
	})
});