GOOGLE_WORKSPACE_MIMETYPES = {
    "Docs": "application/vnd.google-apps.document",
    "Sheets": "application/vnd.google-apps.spreadsheet",
    "Slides": "application/vnd.google-apps.presentation",
    "Drawings": "application/vnd.google-apps.drawing",
    "Jamboard": "application/vnd.google-apps.jam",
}

EXPORT_OPTIONS = {
    "application/vnd.google-apps.document": ["PDF", "Word", "OpenOffice Writer"],
    "application/vnd.google-apps.spreadsheet": ["PDF", "Excel", "OpenOffice Calc"],
    "application/vnd.google-apps.presentation": ["PDF", "PowerPoint", "OpenOffice Impress"],
    "application/vnd.google-apps.drawing": ["PNG", "PDF", "JPEG", "SVG"],
    "application/vnd.google-apps.jam": ["PDF"]
}

EXPORT_MIMETYPES = {
    "PDF": "application/pdf",
    "Word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "Excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "PowerPoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "SVG": "image/svg+xml",
    "HTML": "text/html",
    "Plain Text": "text/plain",
    "OpenOffice Writer": "application/vnd.oasis.opendocument.text",
    "OpenOffice Calc": "application/vnd.oasis.opendocument.spreadsheet",
    "OpenOffice Impress": "application/vnd.oasis.opendocument.presentation"
}

MIMETYPE_EXTENSIONS = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx", 
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx", 
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx", 
    "application/pdf": ".pdf", 
    "image/jpeg": ".jpg", 
    "image/png": ".png", 
    "image/svg+xml": ".svg", 
    "application/vnd.oasis.opendocument.text": ".odt", 
    "application/vnd.oasis.opendocument.spreadsheet": ".ods", 
    "application/vnd.oasis.opendocument.presentation": ".odp"
}

# MIMETYPE_TO_EXPORT_LINK = {
#     "application/vnd.google-apps.document": 
#     "application/vnd.google-apps.spreadsheet": ["PDF", "Excel", "OpenOffice Calc"],
#     "application/vnd.google-apps.presentation": ["PDF", "PowerPoint", "OpenOffice Impress"],
# }

DISCOVERY_SERVICE_URL = 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'

SCOPES = ['https://www.googleapis.com/auth/drive']
