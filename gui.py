import sys

if __name__ == '__main__':
    print('Please run main.py to start the program!')
    sys.exit()

import os
import platform
import traceback
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font
import tkinter.messagebox

# for PyInstaller binaries
try:
    temp_path = sys._MEIPASS
except AttributeError:
    temp_path = os.getcwd()

# TODO: add more main modules here
import json
import urllib.request
import threading
import webbrowser
import configparser

pg_name = 'GWE\'s TkTemplate'  # program name here

username = 'gamingwithevets'  # GitHub username here
repo_name = 'tktemplate'  # GitHub repository name here

version = '1.1.0'  # displayed version (e.g. 1.0.0 Prerelease - must match GH release title)
internal_version = 'v1.1.0'  # internal version (must match GitHub release tag)
prerelease = False  # prerelease flag (must match GitHub release's prerelease flag)


def report_error(self=None, exc=None, val=None, tb=None, term=True):
    """
    Logs in the console and displays a dialog box showing the error.
    Replaces the report_callback_exception() function in
    the tkinter.Tk class.
    NOTE: DO NOT REMOVE THE UNUSED ARGUMENTS! Due to the function replacement
    these arguments must be added.
    """

    e = traceback.format_exc()
    err_text = f'''\
Whoops! An error has occurred.
{e}
If this error persists, please report it here:
https://github.com/{username}/{repo_name}/issues\
'''

    print(err_text)
    tk.messagebox.showerror('Whoops!', err_text)
    if term:
        sys.exit()


tk.Tk.report_callback_exception = report_error


class GUI:
    def __init__(self, window):
        self.version = version

        self.window = window

        self.temp_path = temp_path

        # change width and height of window here
        self.display_w = 800
        self.display_h = 600

        # TODO: add more "open" bools for other Toplevel classes
        self.updater_win_open = False

        tk_font = tk.font.nametofont('TkDefaultFont').actual()
        self.font_name = tk_font['family']
        self.font_size = tk_font['size']

        # TODO: add more font styles (italic, condensed, etc.)
        self.bold_font = (self.font_name, self.font_size, 'bold')

        self.init_window()
        self.init_protocols()

        # TODO: add settings here

        # updater settings
        self.auto_check_updates = tk.BooleanVar()
        self.auto_check_updates.set(True)
        self.check_prerelease_version = tk.BooleanVar()
        self.check_prerelease_version.set(False)

        self.enable_rbin_metadata_unsupported_version_msg = False

        # gets appdata folder
        if os.name == 'nt':
            self.appdata_folder = f'{os.getenv("LOCALAPPDATA")}\\{pg_name}'
        else:
            if platform.system() == 'Darwin':
                self.appdata_folder = os.path.expanduser(f'~/Library/Application Support/{pg_name}')
            else:
                self.appdata_folder = os.path.expanduser(f'~/.config/{pg_name}')

        self.save_to_cwd = False
        self.ini = configparser.ConfigParser()
        self.parse_settings()

        self.refreshing = True

        self.updater = Updater()  # the updater does not need the GUI class as it runs independently of it.
        self.UpdaterGUI = UpdaterGUI(self)

        self.unsupported_tcl = False
        if sys.version_info < (3, 7, 6):
            if tk.messagebox.askyesno('Warning', f'''
It looks like you are running Python {platform.python_version()}, which has a version of Tcl/Tk that doesn\'t support \
some Unicode characters.

Do you want to continue?\
''', icon='warning'):
                self.unsupported_tcl = True
            else:
                self.quit()

        self.menubar()

    def start_main(self):
        """
        Runs necessary commands before calling the main function.
        """

        # TODO: add more commands here
        if self.auto_check_updates.get():
            self.UpdaterGUI.init_window(True)
        self.main()

    def parse_settings(self):
        """
        Loads the program settings.
        """

        # load override settings
        if os.path.exists(os.path.join(os.getcwd(), 'settings.ini')):
            self.ini.read('settings.ini')
            self.save_to_cwd = True
        else:
            # load normal settings
            self.ini.read(f'{self.appdata_folder}\\settings.ini')

        sects = self.ini.sections()
        if sects:
            if 'settings' in sects:
                # TODO: add commands for loading settings
                pass

            if 'updater' in sects:
                try:
                    self.auto_check_updates.set(self.ini.getboolean('updater', 'auto_check_updates'))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    pass
                try:
                    self.check_prerelease_version.set(self.ini.getboolean('updater', 'check_prerelease_version'))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    pass

        self.save_settings()

    def save_settings(self):
        """
        Saves the program settings.
        """

        # settings are set individually to retain compatibility between versions
        self.ini['settings'] = {}
        # TODO: add commands for saving settings

        self.ini['updater'] = {}
        self.ini['updater']['auto_check_updates'] = str(self.auto_check_updates.get())
        self.ini['updater']['check_prerelease_version'] = str(self.check_prerelease_version.get())

        if self.save_to_cwd:
            with open(os.path.join(os.getcwd(), 'settings.ini'), 'w') as f:
                self.ini.write(f)

        if not os.path.exists(self.appdata_folder):
            os.makedirs(self.appdata_folder)
        with open(f'{self.appdata_folder}\\settings.ini', 'w') as f:
            self.ini.write(f)

    @staticmethod
    def n_a():
        """
        Used to prevent access to unimplemented or unfinished features.
        """

        tk.messagebox.showinfo('Not implemented',
                               f'This feature is not implemented into this version of {pg_name}. Sorry!')

    def refresh(self, load_func=False):
        """
        Deletes all widgets and call the main function (if load_func is True).
        """

        self.refreshing = True

        for w in self.window.winfo_children():
            w.destroy()
        self.menubar()

        self.window.protocol('WM_DELETE_WINDOW', self.quit)

        if load_func:
            self.main()

    def set_title(self, custom_str=None):
        """
        Sets the Tkinter window title.
        """

        self.window.title(f'{pg_name} {version}{" - " + custom_str if custom_str is not None else ""}')

    def init_window(self):
        """
        Initializes the Tkinter window.
        """

        self.window.geometry(f'{self.display_w}x{self.display_h}')
        self.window.bind('<F5>', lambda: self.refresh(True))
        self.window.bind('<F12>', self.version_details)
        self.window.option_add('*tearOff', False)
        self.set_title()
        # TODO: uncomment this when you actually have an icon.ico file

    #         try:
    #             self.window.iconbitmap(f'{self.temp_path}\\icon.{"ico" if os.name == "nt" else "xbm"}')
    #         except tk.TclError:
    #             err_text = f'''\
    # Whoops! The icon file "icon.ico" is required.
    # Can you make sure the file is in "{self.temp_path}"?
    # {traceback.format_exc()}
    # If this problem persists, please report it here:
    # https://github.com/{username}/{repo_name}/issues\
    # '''
    #             print(err_text)
    #             tk.messagebox.showerror('Hmmm?', err_text)
    #             sys.exit()

    def init_protocols(self):
        """
        Initializes protocols.
        """

        self.window.protocol('WM_DELETE_WINDOW', self.quit)

    def quit(self):
        """
        Quits the program.
        """

        if not any([
            self.updater_win_open,
            # TODO: add other "open" bools here
        ]):
            # avoids SystemExit exceptions
            os._exit(0)

    @staticmethod
    def about_menu():
        """
        Shows basic information about the version, system and architecture, as well as the license of the project.
        NOTE: LICENSE CANNOT BE CHANGED, AS PER THE CONDITIONS OF THE GNU GPL-V3 LICENSE.
        """

        nl = '\n'
        syst = platform.system()
        syst += ' x64' if platform.machine().endswith('64') else ' x86'
        tk.messagebox.showinfo(f'About {pg_name}', f'''\
{pg_name} - {version} ({'64' if sys.maxsize > 2 ** 31 - 1 else '32'}-bit) - Running on {syst}
Project page: https://github.com/{username}/{repo_name}
{nl + 'WARNING: This is a pre-release version, therefore it may have bugs and/or glitches.' + nl if prerelease else ''}
Licensed under the GNU GPL-v3 license
(LICENSE file available on the GitHub repository or included with source code)\
''')

    def version_details(self, event=None):
        """
        Shows technical information about the Python installation and operating system.
        By default, it can be triggered via the F12 key.
        Note: DO NOT REMOVE THE event ARGUMENT!
        """

        dnl = '\n\n'
        tk.messagebox.showinfo(f'{pg_name} version details', f'''\
{pg_name} {version}{" (prerelease)" if prerelease else ""}
Internal version: {internal_version}

Python version information:
Python {platform.python_version()} ({'64' if sys.maxsize > 2 ** 31 - 1 else '32'}-bit)
Tkinter (Tcl/Tk) version {self.window.tk.call('info', 'patchlevel')}\
{" (most Unicode chars not supported)" if self.unsupported_tcl else ""}

Operating system information:
{platform.system()} {platform.release()}
{'NT version: ' if os.name == 'nt' else ''}{platform.version()}
Architecture: {platform.machine()}{dnl + "Settings file is saved to working directory" if self.save_to_cwd else ""}\
''')

    def menubar(self):
        """
        Sets up the menubar.
        """

        menubar = tk.Menu()

        # TODO: set up the menubar
        file_menu = tk.Menu(menubar)
        file_menu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=file_menu)

        settings_menu = tk.Menu(menubar)
        # TODO: add more setting options
        updater_settings_menu = tk.Menu(settings_menu)
        updater_settings_menu.add_checkbutton(label='Check for updates on startup', variable=self.auto_check_updates,
                                              command=self.save_settings)
        updater_settings_menu.add_checkbutton(label='Check for pre-release versions',
                                              variable=self.check_prerelease_version,
                                              command=self.save_settings)
        settings_menu.add_cascade(label='Updates', menu=updater_settings_menu)

        menubar.add_cascade(label='Settings', menu=settings_menu)

        help_menu = tk.Menu(menubar)
        help_menu.add_command(label='Check for updates', command=self.UpdaterGUI.init_window)
        help_menu.add_command(label=f'About {pg_name}', command=self.about_menu)
        menubar.add_cascade(label='Help', menu=help_menu)

        self.window.config(menu=menubar)

    def main(self):
        """
        Where the mainloop is called.
        """

        ttk.Label(text='GWE\'s TkTemplate', font=self.bold_font).pack()
        ttk.Label(
            text='''\
Hello! This is a simple Tkinter template, with built-in functions such as
an updater and a menubar.

Based on the RBEditor codebase\
''',
            justify='center').pack()

        self.set_title()
        self.window.mainloop()


# TODO: add some other classes here


class UpdaterGUI:
    def __init__(self, gui):
        self.gui = gui

        self.auto = False
        self.after_ms = 100

    def init_window(self, auto=False):
        if not self.gui.updater_win_open:
            self.gui.updater_win_open = True

            if auto:
                self.auto = True

            self.updater_win = tk.Toplevel(self.gui.window)
            self.updater_win.geometry('300x120')
            self.updater_win.resizable(False, False)
            self.updater_win.protocol('WM_DELETE_WINDOW', self.quit)
            self.updater_win.title('Updater')
# TODO: uncomment this when you actually have an icon.ico and icon.xbm file
#             try:
#                 self.updater_win.iconbitmap(f'{self.gui.temp_path}\\icon.{"ico" if os.name == "nt" else "xbm"}')
#             except tk.TclError:
#                 err_text = f'''\
# Whoops! The icon file "icon.ico" is required.
# Can you make sure the file is in "{self.gui.temp_path}"?
# {traceback.format_exc()}
# If this problem persists, please report it here:
# https://github.com/{username}/{repo_name}/issues\
# '''
#                 print(err_text)
#                 tk.messagebox.showerror('Hmmm?', err_text)
#                 sys.exit()

            if self.auto:
                self.updater_win.withdraw()
                self.gui.set_title('Checking for updates...')
            self.updater_win.focus()
            self.updater_win.grab_set()
            self.main()

    def quit(self):
        self.updater_win.grab_release()
        self.updater_win.destroy()
        self.gui.updater_win_open = False
        if self.auto:
            self.auto = False
            self.gui.main()

    def main(self):
        self.update_thread = ThreadWithResult(target=self.gui.updater.check_updates,
                                              args=(self.gui.check_prerelease_version.get(),))

        self.draw_check()
        self.updater_win.after(1, self.start_thread)
        self.updater_win.mainloop()

    def start_thread(self):
        self.update_thread.start()
        while self.update_thread.is_alive():
            self.updater_win.update_idletasks()
            self.progressbar['value'] = self.gui.updater.progress
        self.progressbar['value'] = 100
        self.update_thread.join()
        update_info = self.update_thread.result

        if update_info['error']:
            if update_info['exceeded']:
                self.draw_msg('GitHub API rate limit exceeded! Please try again later.')
            elif update_info['nowifi']:
                self.draw_msg(
                    'Unable to connect to the internet. Please try again\nwhen you have a stable internet connection.')
            else:
                self.draw_msg('Unable to check for updates! Please try again later.')
        elif update_info['newupdate']:
            self.draw_download_msg(update_info['title'], update_info['tag'], update_info['prerelease'])
        else:
            self.draw_msg('You are already using the latest version.')

    def draw_check(self):
        for w in self.updater_win.winfo_children():
            w.destroy()

        ttk.Label(self.updater_win, text='Checking for updates...').pack()
        self.progressbar = ttk.Progressbar(self.updater_win, orient='horizontal', length=100, mode='determinate')
        self.progressbar.pack()
        ttk.Label(self.updater_win, text='DO NOT close the program\nwhile checking for updates',
                  justify='center', font=self.gui.bold_font).pack(side='bottom')

    def draw_msg(self, msg):
        if self.auto:
            self.gui.set_title()
            self.quit()
        else:
            for w in self.updater_win.winfo_children():
                w.destroy()
            ttk.Label(self.updater_win, text=msg, justify='center').pack()
            ttk.Button(self.updater_win, text='Back', command=self.quit).pack(side='bottom')

    def draw_download_msg(self, title, tag, prever):
        if self.auto:
            self.updater_win.deiconify()
            self.gui.set_title()
        for w in self.updater_win.winfo_children():
            w.destroy()
        ttk.Label(self.updater_win, justify='center', text=f'''\
An update is available!')
Current version: {self.gui.version}{" (pre-release)" if prerelease else ""}
New version: {title}{" (pre-release)" if prever else ""}\
''')
        ttk.Button(self.updater_win, text='Cancel', command=self.quit).pack(side='bottom')
        ttk.Button(self.updater_win, text='Visit download page',
                   command=lambda: self.open_download(tag)).pack(side='bottom')

        if self.auto:
            self.updater_win.deiconify()

    def open_download(self, tag):
        webbrowser.open_new_tab(f'https://github.com/{username}/{repo_name}/releases/tag/{tag}')
        self.quit()


class Updater:
    def __init__(self):
        self.username, self.reponame = username, repo_name
        self.request_limit = 5

        self.progress = 0
        self.progress_inc = 25

    def check_internet(self):
        try:
            self.request('https://google.com', True)
            return True
        except Exception:
            return False

    def request(self, url, testing=False):
        success = False
        for i in range(self.request_limit):
            try:
                r = urllib.request.urlopen(url)
                success = True
                break
            except Exception:
                if not testing:
                    if not self.check_internet():
                        return
        if success:
            if not testing:
                d = r.read().decode()
                return json.loads(d)

    def check_updates(self, pr):
        self.progress = 0

        if not self.check_internet():
            return {
                'newupdate': False,
                'error': True,
                'exceeded': False,
                'nowifi': True
            }
        try:
            versions = []
            if not self.check_internet():
                return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}

            response = self.request(f'https://api.github.com/repos/{self.username}/{self.reponame}/releases')
            if response is None:
                return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}

            for info in response:
                versions.append(info['tag_name'])

            # UPDATE POINT 1
            self.progress += self.progress_inc

            if internal_version not in versions:
                try:
                    testvar = response['message']
                    if 'API rate limit exceeded for' in testvar:
                        return {
                            'newupdate': False,
                            'error': True,
                            'exceeded': True
                        }
                    else:
                        return {'newupdate': False, 'error': False}
                except Exception:
                    return {'newupdate': False, 'error': False}
            if not self.check_internet():
                return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}

            # UPDATE POINT 2
            self.progress += self.progress_inc

            response = self.request(
                f'https://api.github.com/repos/{self.username}/{self.reponame}/releases/tags/{internal_version}')
            if response is None:
                return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}
            try:
                testvar = response['message']
                if 'API rate limit exceeded for' in testvar:
                    return {
                        'newupdate': False,
                        'error': True,
                        'exceeded': True
                    }
                else:
                    return {'newupdate': False, 'error': False}
            except Exception:
                pass

            currvertime = response['published_at']

            # UPDATE POINT 3
            self.progress += self.progress_inc

            if not pr:
                if not self.check_internet():
                    return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}

                response = self.request(f'https://api.github.com/repos/{self.username}/{self.reponame}/releases/latest')
                if response is None:
                    return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}
                try:
                    testvar = response['message']
                    if 'API rate limit exceeded for' in testvar:
                        return {
                            'newupdate': False,
                            'error': True,
                            'exceeded': True
                        }
                    else:
                        return {'newupdate': False, 'error': False}
                except Exception:
                    pass
                if response['tag_name'] != internal_version and response['published_at'] > currvertime:
                    return {
                        'newupdate': True,
                        'prerelease': False,
                        'error': False,
                        'title': response['name'],
                        'tag': response['tag_name']
                    }
                else:
                    return {
                        'newupdate': False,
                        'unofficial': False,
                        'error': False
                    }
            else:
                for ver in versions:
                    if not self.check_internet():
                        return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}

                    response = self.request(
                        f'https://api.github.com/repos/{self.username}/{self.reponame}/releases/tags/{ver}')
                    if response is None:
                        return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': True}
                    try:
                        testvar = response['message']
                        if 'API rate limit exceeded for' in testvar:
                            return {
                                'newupdate': False,
                                'error': True,
                                'exceeded': True
                            }
                        else:
                            return {'newupdate': False, 'error': True, 'exceeded': False, 'nowifi': False}
                    except Exception:
                        pass
                    if currvertime < response['published_at']:
                        return {
                            'newupdate': True,
                            'prerelease': response['prerelease'],
                            'error': False,
                            'title': response['name'],
                            'tag': response['tag_name']
                        }
                    else:
                        return {
                            'newupdate': False,
                            'unofficial': False,
                            'error': False
                        }
        except Exception:
            return {
                'newupdate': False,
                'error': True,
                'exceeded': False,
                'nowifi': False
            }


# https://stackoverflow.com/a/65447493
class ThreadWithResult(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        if kwargs is None:
            kwargs = {}

        def function(): self.result = target(*args, **kwargs)

        super().__init__(group=group, target=function, name=name, daemon=daemon)
