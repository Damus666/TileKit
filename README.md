# Tile Kit

A tile editor made in python with pygame.

Implements: layers, tiles, objects, tools, saving, menu and exporting to JSON

There is also the <code>pytilekit.py</code> module that can read an exported JSON and convert it to python objects to use in games

# How to use it

Run the editor running <code>tilekit.py</code> with <code>python 3.10+</code> and <code>pygame 2.1+</code>

Use the module importing <code>pytilekit.py</code> into your project and calling the <code>load()</code> function passing the <code>TextIOWrapper</code> of the exported JSON

If you use another language you can parse the save yourself, considering the JSON is structured like this:
<pre><code>
{
    "settings":{
        "tile_size":tilesize,
        "map_size":[msx,msy]
    },

    "tiles":[
        {
            "id":id,
            "path":filepathname,
            "type":type // tile or object
        } // for every tile and object data
    ],

    "layers":[
        {
            "name":name,
            "visible":visible,
            "tiles":[
                {
                    "id":tileid,
                    "position":[absposx,absposy]
                } // for every tile and object in the layer
            ]
        } // for every layer
    ]
}
</code></pre>