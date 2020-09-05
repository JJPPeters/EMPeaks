# from GUI.Modules.menu_entry_module import MenuEntryModule
# from Processing.DisplacementAnalysis import ABO_ca_ratio
# from GUI.Dialogs.process_settings_dialog import ProcessSettingsDialog
# from GUI import ImageWindow
# from GUI.Controls.Plot.Plottables import ImagePlot
#
# base_path = ['Process', 'Map', 'Lattice']
#
#
# class CellRatio(MenuEntryModule):
#     def __init__(self):
#         self.menu_structure = base_path
#         self.name = 'c/a ratio'
#         self.order_priority = 0
#
#     def run(self):
#         # These need to be selected by user
#         Acol = 'sub0'
#         Bcol = 'sub1'
#
#         Adata = self.main_window.last_active.plottables[Acol].points
#         Bdata = self.main_window.last_active.plottables[Bcol].points
#         shp = self.active_image_window.image_plot.image_data.shape
#         title = self.main_window.last_active.name
#
#         if Adata is not None and Bdata is not None:
#             ratio = ABO_ca_ratio(Adata, Bdata, shp[0], shp[1])
#
#             image_id = self.main_window.generate_window_id()
#             new_image_window = ImageWindow(title + ' c/a ratio', image_id, master=self.main_window)
#             new_image_window.show()
#             image = ImagePlot(ratio)
#             new_image_window.set_image_plot(image)
#
#             self.main_window.Children[image_id] = new_image_window
