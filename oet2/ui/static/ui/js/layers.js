/*
 * Configuration for base layers.
 */
var Layers = {};

Layers.OSM = new ol.layer.Tile({
    title: "OpenStreetMap",
    source: new ol.source.OSM()})
//Layers.OSM = new OpenLayers.Layer.OSM("OpenStreetMap");


Layers.HOT = new ol.layer.Tile({
    source: new ol.source.XYZ({
        url: ["//a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
            "//b.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
            "//c.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"]
})
});

//Layers.HOT = new OpenLayers.Layer.XYZ("Humanitarian OSM",
 //               ["//a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
 //                "//b.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
 //                "//c.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
 //               ],
 //               {
 //                   isBaseLayer: true,
 //                   sphericalMercator: true,
 //               }
 //           );
