__version__ = "0.1.0"
# from edider.x11read import (
#     get_output_edid as _get_output_edid,
#     get_screen_resolution as _get_screen_resolution,
# )

# from edider.parser import EDIDParser as _EDIDParser

# class Screen(object):
#     def __init__(self, index=0):
#         self.index = index

#     @property
#     def edid(self):
#         try:
#             return self._edid
#         except AttributeError:
#             edid = _get_output_edid(self.index)
#             self._edid = edid
#             return edid

#     def _set_resolution(self):
#         x, y = _get_screen_resolution(self.index)
#         self._width_in_pixels, self._height_in_pixels = x, y
        
#     @property
#     def height_in_pixels(self):
#         try:
#             return self._height_in_pixels
#         except AttributeError:
#             self._set_resolution()
#             return self._height_in_pixels

#     @property
#     def width_in_pixels(self):
#         try:
#             return self._width_in_pixels
#         except AttributeError:
#             self._set_resolution()
#             return self._width_in_pixels

#     @property
#     def manufacturer_id(self):
#         return _EDIDParser(self.edid).manufacturer_id

#     @property
#     def manufacture_year(self):
#         return _EDIDParser(self.edid).manufacture_year

#     @property
#     def width_in_cm(self):
#         return _EDIDParser(self.edid).horizontal_size

#     @property
#     def height_in_cm(self):
#         return _EDIDParser(self.edid).vertical_size

#     @property
#     def misc(self):
#         edp = _EDIDParser(self.edid)
#         desc = [
#             edp.descriptor1,
#             edp.descriptor2,
#             edp.descriptor3,
#             edp.descriptor4,
#         ]
#         desc = [x for x in desc if x]
#         desc = '; '.join(desc)
#         return desc

#     def __repr__(self):
#         cname = self.__class__.__name__
#         return cname + '({})'.format(self.index)

#     def __str__(self):
#         cname = self.__class__.__name__
#         return cname + '({})'.format(self.index)
        
