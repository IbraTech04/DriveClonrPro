# DriveClonrPro
## About DriveClonrPro
Alas! The successor to the absolute mess of a codebase known as DriveClonr. Oh, and it has a GUI now ^_^. DriveClonr was a MESS due to the timecrunch I built it under; I found a bug with how I was using the NextPageTokens and fixing it required a lot of code rewriting. Since my school Google Drive was at risk of being disabled at any moment, I took the lazy approach and wrote really basic patches to get by.... patches that remain to this day. I had plans to fix DriveClonr but never got around to it, until now! 

DriveClonrPro is a new take on the DriveClonr legacy, adding a GUI, proper OOP design, and a lot of other cool stuff. It's still in development, but it's already a lot better than DriveClonr.

## Key differences between DriveClonr and DriveClonrPro
1. DriveClonrPro uses Tkinter to create a basic GUI for the user to interact with. This makes it a lot easier to use than DriveClonr, which required the user to interact with the program through the terminal. I would've used PyQT5, but I've had trouble getting that to work on macOS, so I decided to go with Tkinter instead.

2. DriveClonrPro allows the user to modify what each Google Workspace document type is converted to. For example, the user can choose to convert all Google Docs to Microsoft Word documents and all Google Sheets to PDF documents; You're no longer stuck with either-or. This is a feature that was requested by a user of DriveClonr, and I'm glad to finally be able to implement it.

3. DriveClonrPro allows the user to select whether to clone their drive, shared files, trashed files, or all three; No longer are you stuck with cloning your entire drive. This is a feature that I wish I had added to the original DriveClonr, but I never got around to it. Nonetheless, it's here now! You can select which files to clone by selecting the checkboxes next to each option.
Coming Soon: A proper TreeView widget that allows the user to select which folders to clone. You can see the beginnings of this in the TreeViewer class, but I'm having some problems with it that I need to fix before I can add it to the program.

4. DriveClonrPro is (eventually going to be) multithreaded! This means that the program will be able to clone multiple files at once, making the cloning process a lot faster. This is a feature that I wanted to add to DriveClonr, but I never got around to it. I'm still working on this feature, but it's coming along nicely.

5. DriveClonrPro has a proper logo. The Original DriveClonr never had a logo, so I figured it was time to design a proper one. I took some inspiration from Icons8 Fluent Design icons and Designed my own in Adobe Illustrator. I'm pretty happy with how it turned out.

## How to use DriveClonrPro

### Prerequisites
1. Python 3.9 or higher (I personally test this with Python 3.9.13, but it should work with any version of Python 3.9 or higher)
2. The Google Drive API Python Library (Install with `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`)
3. Valid Google Drive API Credentials (See [this page](https://developers.google.com/workspace/guides/create-credentials) for more information on how to get these. This application requires OAuth 2.0 credentials, so make sure you create a JSON file with the credentials and place it in the same directory as the program. The code assumes the file is called `creds.json` but you can change this in the code if you want to.)
4. A Drive you want to clone! 

### Installation
1. Download precompiled binaries (if they exist) or clone this repository to your computer. Make sure to install dependencies (see `requirements.txt`) if you're cloning the repository.
2. Place your `creds.json` file in the same directory as the program.
3. Run `MainWindow.py` and follow the instructions on screen. It's that simple! 

## Known Issues
1. DriveClonrPro does not check for ample space before cloning. This is something I aim to rectify in the future.
2. Any exception within the Google Drive API will cause DriveClonrPro to crash. This is something I aim to rectify in the future.
3. Tkinter seems to not like the cloning screen; The layout of the objects moves around a lot when the length of the file name changes. This is something I aim to rectify in the future.

## Features:

1. Auto LongFilePaths enabler on Windows
    To avoid complex file-path size trimming, DriveClonrPro automatically enables the LongFilePaths registry key on Windows. This allows DriveClonrPro to clone files with long file names without any issues. This feature is only available on Windows, as macOS and Linux do not have a file name length limit.

2. Unmatched Google Workspace Support
    New with DriveClonrPro is the ability to specify what each type of Google Workspace document is converted to. For example, you can choose to convert all Google Docs to Microsoft Word documents and all Google Sheets to PDF documents. Unlike the legacy DriveClonr, you're no longer stuck with either-or. 

3. Direct-Download. 
    Unlike manually selecting files from Google Drive, DriveClonrPro directly downloads the files from Google Drive without the need for a compression intermediary. This means that you don't have to worry about Google Drive's download limits - And also get instant access to your files :P

## Planned Features:

1. Multithreading
    DriveClonrPro will be multithreaded, allowing it to clone multiple files at once. This will make the cloning process a lot faster. This feature is currently in development.

2. TreeView Widget
    DriveClonrPro will have a proper TreeView widget that allows the user to select which folders to clone. This feature is currently in development.

3. Dark Mode
    DriveClonrPro will have a dark mode - Like basically every other program nowadays. This feature is currently in development.

4. Better Error Handling
    Currently, DriveClonrPro will crash if any exception is thrown within the Google Drive API. This is something I aim to fix in the future.

5. Better Space Checking
    Currently, DriveClonrPro does not check for ample space before cloning. This is something I aim to fix in the future.