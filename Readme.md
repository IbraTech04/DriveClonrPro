# DriveClonrPro

The BEST way to clone your Google Drive files to your computer.

## About DriveClonrPro

Alas! The successor to the absolute mess of a codebase known as DriveClonr has emerged! Oh, and it has a GUI now ^_^. DriveClonr was a MESS due to the time-crunch I built it under; Long-story-short: I found a bug with how I was using `NextPageTokens` and fixing it required a lot of code rewriting. Since my school Google Drive was at risk of being disabled at any moment, I took the lazy approach and wrote really basic patches to get by.... patches that remain to this day. I had plans to fix DriveClonr but never got around to it, until now!

DriveClonrPro is a new take on the DriveClonr legacy, adding a GUI, proper OOP design, and a lot of other cool stuff. It's still in development, but it's already a lot better (and more importantly, stable) than DriveClonr.

## What happened to the `e` in DriveClon(e)rPro?

Simply put, `Clonr` looks cooler than `Cloner`. This was a decision made late at night one faithful day during the original development of DriveClonr, and I'm sticking with it.

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
3. Anything else in `requirements.txt` (Install with `pip install -r requirements.txt`)
4. Valid Google Drive API Credentials (See [this page](https://developers.google.com/workspace/guides/create-credentials) for more information on how to get these. This application requires OAuth 2.0 credentials, so make sure you create a JSON file with the credentials and place it in the `/assets` directory. The code assumes the file is called `creds.json` but you can change this in the code if you want to.)
5. A Google Drive account with files to clone (duh)

### Installation

1. Download precompiled binaries (if they exist) or clone this repository to your computer. Make sure to install dependencies (see `requirements.txt`) if you're cloning the repository.
2. Place your `creds.json` file in the `/assets` directory. This file contains your Google Drive API credentials and is required for the program to work. If you don't have this file, the program will not work. You can get this file by following the instructions [here](https://developers.google.com/workspace/guides/create-credentials).
3. Run `app.py` in your terminal or command prompt. This will start the program and open the GUI. If you're using Windows, you can also run `app.bat` to start the program. This will automatically set the LongFilePaths registry key for you.

## How does DriveClonrPro work?

Simply put, I treat the Google Drive file structure like a massive tree and recurse through it using Postorder traversal, creating each folder as I recurse deeper. This would normally be a fast process, however each level of recursion requires a new call to the Google Drive API which slows down the process.

I'm not sure why I chose postorder traversal, but it works so I'm not complaining :shrug:. In hindsight I should've used level-order traversal, but if it works, it works.

## Known Issues

1. Tkinter seems to not like the cloning screen; The layout of the objects moves around a lot when the length of the file name changes. This is something I aim to rectify in the future.
2. The UI doesn't scale properly; it becomes blurry when scaled up. This is probably an issue with Tkinter that I don't think I can fix easily

## Features

1. Auto LongFilePaths enabler on Windows
    - To avoid complex recursive file-path size trimming, DriveClonrPro automatically enables the LongFilePaths registry key on Windows. This allows DriveClonrPro to clone files with long file names without any issues. This feature is only available on Windows, as macOS and Linux do not have a file name length limit (Unix go brrr).

2. Unmatched Google Workspace Support
    - New with DriveClonrPro is the ability to specify what each type of Google Workspace document is converted to. For example, you can choose to convert all Google Docs to Microsoft Word documents and all Google Sheets to PDF documents. Unlike the legacy DriveClonr, you're no longer stuck with either-or.

3. Direct-Download
    - Unlike manually selecting files from Google Drive, DriveClonrPro directly downloads the files from Google Drive without the need for a compression intermediary (like .zip). This means that you don't have to worry about Google Drive's download limits - And also get instant access to your files :P

4. Cross-platform
    - A feature completely in the control of Tkinter and Python, I'm taking credit for it regardless :P. DriveClonrPro is cross-platform, meaning it works on Windows, macOS, and Linux. Granted, I've only tested it on Windows, but by PSMI (Pure Software MagIc™) it should work on macOS and Linux as well.

5. Complete filesize support
    - Unlike its predecessor, DriveClonrPro supports cloning files of any size - Specifically exported Google Workspace documents. Whereas DriveClonr would have failed at cloning the file, DriveClonrPro is able to use export links to bypass the export limit and clone the file.

## Planned Features

1. Multithreading
    - DriveClonrPro will be multithreaded, allowing it to clone multiple files at once. This will make the cloning process a lot faster. This feature is currently in development.

2. TreeView Widget
    - DriveClonrPro will have a proper TreeView widget that allows the user to select which folders to clone. This feature is currently in development.

3. Dark Mode
    - DriveClonrPro will have a dark mode - Like basically every other program nowadays. This feature is currently in development.

4. Better Error Handling
    - Currently, DriveClonrPro isn't equipped to handle every possible error. I aim to add more recoverable errors in the future.

5. Shared Drive Support
    - DriveClonrPro will support cloning files from Shared Drives. This feature is currently in development.

6. Google Photos Cloning Support
    - If you're anything like me, you love having offline backups of your photos. At some point, I'd like to add support for cloning Google Photos to DriveClonrPro - This will definitely tie into the multithreading feature.

7. More Personalized UI
    - I am lazy, and as such did not utilize the Google People API in this application at all. At some point, I'd like to utilize this API to make the UI more personalized to the user (i.e, name, profile picture, etc.)

8. Language Support
    - At some point I'd like to add support for languages other than English - Mostly as a challenge to myself but also to make DriveClonr more accessible to non-English speakers.
