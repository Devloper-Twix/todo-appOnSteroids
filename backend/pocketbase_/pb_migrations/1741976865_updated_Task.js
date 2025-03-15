/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3577811883")

  // update collection data
  unmarshal({
    "name": "tasks"
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3577811883")

  // update collection data
  unmarshal({
    "name": "Task"
  }, collection)

  return app.save(collection)
})
