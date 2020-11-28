from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog

import GUI
from GUI.Controls.Plot.Plottables import ImagePlot


import re

class InvertModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image']
        self.name = 'Arithmetic'
        self.order_priority = 0

    def run(self):
        if not self.open_image_window_ids:
            return

        # create parameters for dialog
        text = ["LineEdit", 0, "Script", ""]

        # runs as modal dlg
        filter_settings = ProcessSettingsDialog(
            master=self.main_window,
            name='Arithmetic',
            function=self.parse,
            inputs=[text],
            show_preview=False, preserve_image=False)

        filter_settings.exec()

    def parse(self, v):

        # strip things like new line characters?

        code = v[0]

        code = "rargs = " + code
        code_parsed = self.parse_code(code)
        arg_dict = self.main_window.children

        rargs = self.code_runner(code_parsed, arg_dict)

        image_id = self.main_window.generate_window_id()
        title = "test"
        image_window = GUI.ImageWindow(title, image_id, master=self.main_window)
        image_window.show()
        image_plot = ImagePlot(rargs, visible=True)
        image_window.set_image_plot(image_plot)

        self.main_window.children[image_id] = image_window

    def parse_code(self, code):

        # this regex matches multiple/single capital letters
        # this is not very comprehensive
        # i.e. it won't handle strings well
        # can add in the " and ' characters but still wont catch AA in the middle of a string (surrounded by spaces)

        # later might want to account for . after the image id to allow it to be used as a direct class
        # and not just for it's data

        # get list of open window ids
        wins = self.open_image_window_ids()


        # return if we have none
        if not wins:
            return code

        # make a list of ids for the regex we will use
        # do this so we can make new variables/windows without having to have those windows already created
        win_string = ""
        for win in wins:
            win_string += win + "|"
        win_string = win_string[:-1]  # remove trailing |

        # make the regex
        pattern = re.compile(r"(?<![A-Za-z_])([" + win_string + r"])(?![A-za-z_])")

        # # get matches (and remove duplicates) to use later?
        # matches = [x.group() for x in re.finditer(pattern, code)]
        # matches = list(dict.fromkeys(matches))

        # replace the code instances with the dictionary we will be using
        code = pattern.sub(r'args["\1"].image_plot.image_data', code)

        return code


    def code_runner(self, code, args):
        largs = locals()

        exec(code, globals(), largs)

        return largs['rargs']
