const logger = require("kaleido-api/logger");

const sendError = require('./send_error');

var fieldmap = {
  name: (design) => design.name,
  description: (design) => design.meta_description,
  creator_name: (design) => design.creator_name,
  config_url: (design) => `https://www.remove.bg/t/${design.slug}`,
  thumbnail_url: (design) => `https://kaleidousercontent.com/removebg/designs/${design.raw_id ? design.raw_id : design.id}/thumbnail_image/${design.thumbnail_image}`,
  script_url: (design) => design.script_url,
  script_data: (design) => design.graph,
  script_inputs: (design) => (design.script_inputs ? design.script_inputs : {}),
};

var queries = {
  allTemplates: (db) => {
    return db.query(`
      SELECT id, name, meta_description, creator_name, slug, thumbnail_image, script_url, graph
      FROM templates
      WHERE published_at < CURRENT_TIMESTAMP
      ORDER BY created_at
    `);
  },
  findTemplate: (db, id) => {
    return db.query(`
      SELECT id, name, meta_description, creator_name, slug, thumbnail_image, script_url, graph
      FROM templates
      WHERE published_at < CURRENT_TIMESTAMP
      AND id = $1
    `, [id]);
  },
  allConfigs: (db, user_id) => {
    return db.query(`
      SELECT id, name, input_values, template_id
      FROM template_configs
      WHERE user_id = $1
      ORDER BY created_at
    `, [user_id]);
  },
  findConfig: (db, user_id, template_id, config_id) => {
    return db.query(`
      SELECT id, name, input_values, template_id
      FROM template_configs
      WHERE user_id = $1
      AND template_id = $2
      AND id = $3
    `, [user_id, template_id, config_id]);
  },
};

function getFieldConfig(req) {
  var fields = ['name'];
  if(req.query && req.query.fields && req.query.fields.design) {
    fields = String(req.query.fields.design).split(',');
  }
  for(var field of fields) {
    if(!(field in fieldmap)) {
      return {
        fields: null,
        error: `Invalid field ${field}. Valid fields are: ${Object.keys(fieldmap).join(', ')}`,
      };
    }
  }
  return {
    fields: fields,
    error: null,
  };
}

function designToJson(design, fieldCfg) {
  var attributes = {};
  fieldCfg.fields.forEach((field) => {
    attributes[field] = fieldmap[field](design);
  });

  return {
    type: "design",
    id: design.id,
    attributes: attributes,
  };
}

function configureDesign(design, config) {
  var base = { ...design };
  if(config) {
    base.name = ` - ${config.name}`;
    base.raw_id = base.id;
    base.id = `${base.id}-tc-${config.id}`;
    base.script_inputs = config.input_values;
  }
  return base;
}

const Design = {
  index: (db, req, res) => {
    var fieldCfg = getFieldConfig(req);
    if(fieldCfg.error) return sendError(res, 400, fieldCfg.error);

    queries.allTemplates(db).then((templateResults) => {
      queries.allConfigs(db, res.locals.user_id).then((configResults) => {
        var configsByTemplateId = {};
        configResults.rows.forEach((config) => {
          if(!configsByTemplateId[config.template_id]) {
            configsByTemplateId[config.template_id] = [];
          }
          configsByTemplateId[config.template_id].push(config);
        });
        var rows = [];
        templateResults.rows.forEach((design) => {
          rows.push(designToJson(design, fieldCfg));
          var configs = configsByTemplateId[design.id];
          if(configs) {
            configs.forEach((config) => {
              rows.push(designToJson(configureDesign(design, config), fieldCfg));
            });
          }
        })

        res.json({ data: rows });
        res.end();
      }).catch((err) => {
        logger.info("Configs fetch error: ", err);
        sendError(res, 500, "Internal error while fetching configs. Please try again later.");
      })
    }).catch((err) => {
      logger.info("Designs fetch error: ", err);
      sendError(res, 500, "Internal error while fetching designs. Please try again later.");
    })
  },

  show: (db, req, res) => {
    var fieldCfg = getFieldConfig(req);
    if(fieldCfg.error) return sendError(res, 400, fieldCfg.error);

    var templateId = String(req.params.id);
    var configId = null;
    var idSplit = templateId.split("-tc-");
    if(idSplit.length > 1) {
      templateId = idSplit[0];
      configId = idSplit[1];
    }

    queries.findTemplate(db, templateId).then((templateResults) => {
      if(templateResults.rows.length == 1) {

        var configureIfRequired = (unconfigured) => {
          return new Promise((resolve, reject) => {
            if(configId) {
              queries.findConfig(db, res.locals.user_id, templateId, configId).then((configResults) => {
                if(configResults.rows.length == 1) {
                  var configured = configureDesign(unconfigured, configResults.rows[0]);
                  resolve(configured);
                }
                else {
                  sendError(res, 404, "Design preset not found");
                }
              }).catch((err) => {
                logger.info("Design presets fetch error: ", err);
                sendError(res, 500, "Internal error while fetching design preset. Please try again later.");
              })
            }
            else {
              resolve(unconfigured);
            }
          })
        }

        var unconfigured = templateResults.rows[0];
        configureIfRequired(unconfigured).then((design) => {
          res.json({ data: designToJson(design, fieldCfg) });
          res.end();
        });
      }
      else {
        sendError(res, 404, "Design not found");
      }
    }).catch((err) => {
      logger.info("Designs fetch error: ", err);
      sendError(res, 500, "Internal error while fetching design. Please try again later.");
    })
  }
}

module.exports = Design;
