/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3577811883")

  // update field
  collection.fields.addAt(6, new Field({
    "hidden": false,
    "id": "select1542800728",
    "maxSelect": 6,
    "name": "tags",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "select",
    "values": [
      "work",
      "personal",
      "shopping",
      "health",
      "finance",
      "education"
    ]
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3577811883")

  // update field
  collection.fields.addAt(6, new Field({
    "hidden": false,
    "id": "select1542800728",
    "maxSelect": 6,
    "name": "field",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "select",
    "values": [
      "work",
      "personal",
      "shopping",
      "health",
      "finance",
      "education"
    ]
  }))

  return app.save(collection)
})
