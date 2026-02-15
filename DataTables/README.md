# Icarus TV Mod — Data Table Entries

These JSON entries must be added to the corresponding game data tables on the server side.
They can be merged using Icarus Mod Manager (IMM) or by manual JSON editing.

Each section below shows the exact entry to append to the Rows array in the corresponding file.

---

## D_ItemsStatic.json

```json
{
    "Name": "TV",
    "Meshable": {
        "RowName": "Mesh_Generic_Fabricator"
    },
    "Itemable": {
        "RowName": "Item_TV"
    },
    "Interactable": {
        "RowName": "Deployable_Power_Toggle_Only"
    },
    "Focusable": {
        "RowName": "Focusable_1H"
    },
    "Highlightable": {
        "RowName": "Generic"
    },
    "Actionable": {
        "RowName": "Deployable"
    },
    "Usable": {
        "RowName": "Place"
    },
    "Deployable": {
        "RowName": "TV"
    },
    "Durable": {
        "RowName": "Deployable_750"
    },
    "Decayable": {
        "RowName": "Decay_10_Minutes"
    },
    "Resource": {
        "RowName": "Electric_Light_Single"
    },
    "Audio": {
        "RowName": "GenericDeployable"
    },
    "Manual_Tags": {
        "GameplayTags": [
            {
                "TagName": "Item.Deployable.TV"
            }
        ]
    }
}
```

---

## D_ItemTemplate.json

```json
{
    "Name": "TV",
    "ItemStaticData": {
        "RowName": "TV"
    }
}
```

---

## D_Itemable.json

```json
{
    "Name": "Item_TV",
    "DisplayName": "NSLOCTEXT(\"D_Itemable\", \"Item_TV-DisplayName\", \"Flat Screen TV\")",
    "Icon": "/Game/Mods/TV/Textures/T_ITEM_TV.T_ITEM_TV",
    "Description": "NSLOCTEXT(\"D_Itemable\", \"Item_TV-Description\", \"A wall-mounted flat screen TV. Requires electricity.\")",
    "FlavorText": "NSLOCTEXT(\"D_Itemable\", \"Item_TV-FlavorText\", \"Now streaming.\")",
    "Weight": 2000
}
```

---

## D_Deployable.json

```json
{
    "Name": "TV",
    "Variants": [
        {
            "RowName": "TV",
            "DataTableName": "D_DeployableSetup"
        }
    ],
    "EffectedByWeather": false
}
```

---

## D_DeployableSetup.json

```json
{
    "Name": "TV",
    "DeployableBlueprint": "/Game/Mods/TV/Blueprints/BP_TV.BP_TV_C",
    "PreviewStaticMesh": "/Game/Mods/TV/Meshes/TV_LG_TV_Frame.TV_LG_TV_Frame",
    "DeployedSound": "/Game/FMOD/Events/SFX/D_Deployables/SFX_DEP_GENERIC.SFX_DEP_GENERIC",
    "MaxSurfaceSnapAngle": 180,
    "SupportsCustomRotation": false,
    "WorldPlacementType": "WallPlacement",
    "bCanAffectNavigation": false,
    "MaxRestackingAmount": 1
}
```

---

## D_Resource.json

The TV reuses the existing `Electric_Light_Single` resource entry (already in the base game) for its power connection. No new entry needed unless you want custom power behavior.

---

## D_ProcessorRecipes.json

```json
{
    "Name": "TV",
    "Requirement": {
        "RowName": "TV"
    },
    "RequiredMillijoules": 15000,
    "RecipeSets": [
        {
            "RowName": "Fabricator",
            "DataTableName": "D_RecipeSets"
        }
    ],
    "Inputs": [
        {
            "Element": {
                "RowName": "Electronics",
                "DataTableName": "D_ItemsStatic"
            },
            "Count": 4
        },
        {
            "Element": {
                "RowName": "Glass",
                "DataTableName": "D_ItemsStatic"
            },
            "Count": 1
        },
        {
            "Element": {
                "RowName": "Aluminium",
                "DataTableName": "D_ItemsStatic"
            },
            "Count": 1
        }
    ],
    "Outputs": [
        {
            "Element": {
                "RowName": "TV",
                "DataTableName": "D_ItemTemplate"
            },
            "Count": 1,
            "DynamicProperties": [],
            "Alterations": []
        }
    ],
    "Audio": {
        "RowName": "CraftingBench"
    }
}
```

---

## D_BlueprintUnlocks.json

Add the TV to whatever tech tree tier you prefer. The exact entry depends on your unlock structure. Example linking to an existing tier:

```json
{
    "Name": "TV",
    "Items": [
        {
            "RowName": "TV",
            "DataTableName": "D_ItemsStatic"
        }
    ]
}
```

Adjust the unlock requirements and tier placement to fit your server's progression.
