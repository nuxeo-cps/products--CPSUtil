import warnings
from Products.CPSUtil.property import PropertiesPostProcessor
from Products.CPSUtil.property import PostProcessingPropertyManagerHelpers

warnings.warn("The module Products.CPSUtil.PropertiesPostProcessor "
              "has been renamed to Products.CPSUtil.property and "
              "will be removed in CPS 3.6",
              DeprecationWarning, 2)

