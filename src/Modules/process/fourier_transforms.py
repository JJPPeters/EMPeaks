from GUI.Modules.menu_entry_module import MenuEntryModule
import numpy as np


class FftModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Process', 'FFT']
        self.name = 'FFT'
        self.order_priority = 0

    def run(self):
        if not self.main_window.image_requirements_met():
            return
        fftmat = np.fft.fftshift(np.fft.fft2(self.main_window.last_active.image_plot.image_data, axes=(0, 1)), axes=(0, 1))

        self.main_window.create_new_image("FFT of " + self.main_window.last_active.name, fftmat)


class IfftMmodule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Process', 'FFT']
        self.name = 'IFFT'
        self.order_priority = 1

    def run(self):
        if not self.main_window.image_requirements_met():
            return
        ifftmat = np.fft.ifft2(np.fft.fftshift(self.main_window.last_active.image_plot.image_data, axes=(0, 1)), axes=(0, 1))

        self.main_window.create_new_image("FFT of " + self.main_window.last_active.name, ifftmat)
