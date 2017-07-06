'use strict';

const electron = require('electron')
const BrowserWindow = electron.BrowserWindow
const path = require('path')
const logger = require('electron-log');
const {app, Menu} = electron

logger.transports.file.level = 'info'
logger.transports.file.file = app.getPath('userData') + '/log.txt'

/*************************************************************
 * py process
 *************************************************************/

const PY_DIST_FOLDER = 'dist'
const PY_FOLDER = 'motiosecure'
const PY_MODULE = 'api' // without .py suffix

let pyProc = null
let pyPort = null

const guessPackaged = () => {
  const fullPath = path.join(__dirname, PY_DIST_FOLDER)
  return require('fs').existsSync(fullPath)
}

const getScriptPath = () => {
  if (!guessPackaged()) {
    return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
  }
  if (process.platform === 'win32') {
    return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE + '.exe')
  }
  return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE, PY_MODULE)
}

const selectPort = () => {
  pyPort = 4242
  return pyPort
}

const createPyProc = () => {
  let script = getScriptPath()
  let port = '' + selectPort()

  if (guessPackaged()) {
    pyProc = require('child_process').execFile(script, [port])
  } else {
    pyProc = require('child_process').spawn('python', [script, port])
  }

  if (pyProc != null) {
    logger.info('Child process started port ' + port)
    pyProc.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
      logger.info(`stdout: ${data}`);
    });

    pyProc.stderr.on('data', (data) => {
      console.log(`stderr: ${data}`);
      logger.error(`stderr: ${data}`);
    });

    pyProc.on('close', (code) => {
      logger.info(`child process exited with code ${code}`);
    });
  }
}

const exitPyProc = () => {
  pyProc.kill()
  pyProc = null
  pyPort = null
}

app.on('ready', createPyProc)
app.on('will-quit', exitPyProc)


/*************************************************************
 * window management
 *************************************************************/

let mainWindow = null

const createWindow = () => {
  mainWindow = new BrowserWindow({width: 1200, height: 600, frame: false})
  mainWindow.loadURL(require('url').format({
    pathname: path.join(__dirname, 'html/index.html'),
    protocol: 'file:',
    slashes: true
  }))
  // mainWindow.webContents.openDevTools()

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  var template = [{
      label: "Application",
      submenu: [
          { label: "About Application", selector: "orderFrontStandardAboutPanel:" },
          { type: "separator" },
          { label: "Quit", accelerator: "Command+Q", click: function() { app.quit(); }}
      ]}, {
      label: "Edit",
      submenu: [
          { label: "Undo", accelerator: "CmdOrCtrl+Z", selector: "undo:" },
          { label: "Redo", accelerator: "Shift+CmdOrCtrl+Z", selector: "redo:" },
          { type: "separator" },
          { label: "Cut", accelerator: "CmdOrCtrl+X", selector: "cut:" },
          { label: "Copy", accelerator: "CmdOrCtrl+C", selector: "copy:" },
          { label: "Paste", accelerator: "CmdOrCtrl+V", selector: "paste:" },
          { label: "Select All", accelerator: "CmdOrCtrl+A", selector: "selectAll:" }
      ]},
      {
        role: 'help',
        submenu: [
          {
            label: 'Learn More',
            click () { electron.shell.openExternal('https://github.com/alvinwan/motiosecure') }
          },
          {
            label: 'About Alvin',
            click () { electron.shell.openExternal('http://alvinwan.com') }
          }
        ]
      }
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})
