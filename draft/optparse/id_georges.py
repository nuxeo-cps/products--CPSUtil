def do_test(test_descriptor):
    """Perform the testing described by descriptor."""
class TestDescriptor(object):
     """Encapsulate a series of options for Zope Test Runner.""""
     def __init__(self, product_name, **options):
       """ par exemple."""
              self.product_name = product_name
          for k, v in options.items():
                  setattr(self, k, v) # unpeu bourrin

jobs = [TestDescriptor(prod_name) for prod_name in products)

def do_test(descriptor):
    os.system('bin/zopectl test --dir Products/%s --option=%s' % (descriptor.product_name, descriptor.option_1))

 results = pool.map(do_test, jobs)
 if False in results:
    print 'BROKEN TESTS (gasp)'
      sys.exit(1)
