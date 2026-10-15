{
  "name": "Real Estate AI - Lead to Google Sheet (WebU)",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "real-estate-lead",
        "responseMode": "responseNode",
        "options": {}
      },
      "id": "webhook-real-estate",
      "name": "Webhook - Real Estate Lead",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [400, 300],
      "webhookId": "real-estate-lead-webu"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://script.google.com/macros/s/AKfycbz8ITyxxiL5wgOp-0DGLUo0MmpkaaR-HgAuinMs-6aiIUzhCwmndnKnVxpO1Xo2bYiSFw/exec",
        "sendBody": true,
        "bodyContentType": "json",
        "jsonBody": "={{ JSON.stringify({name: $json.body?.name || $json.name || 'Unknown', phone: $json.body?.phone || $json.phone || '', BHK: $json.body?.BHK || $json.BHK || '', location: $json.body?.location || $json.location || '', budget: $json.body?.budget || $json.budget || '', timeline: $json.body?.timeline || $json.timeline || '', lead_temperature: $json.body?.lead_temperature || $json.lead_temperature || ''}) }}",
        "options": {
          "redirect": {
            "redirect": "follow"
          }
        }
      },
      "id": "http-request-sheet",
      "name": "Send to Google Sheet",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [720, 300]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={ \"success\": true, \"message\": \"Lead saved to Google Sheet (WebU)\" }",
        "options": {}
      },
      "id": "respond-success",
      "name": "Respond Success",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [1020, 300]
    }
  ],
  "connections": {
    "Webhook - Real Estate Lead": {
      "main": [[{ "node": "Send to Google Sheet", "type": "main", "index": 0 }]]
    },
    "Send to Google Sheet": {
      "main": [[{ "node": "Respond Success", "type": "main", "index": 0 }]]
    }
  },
  "pinData": {},
  "meta": {
    "instanceId": "real-estate-n8n-webu"
  }
}
