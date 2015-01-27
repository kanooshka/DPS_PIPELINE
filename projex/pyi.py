""" 
Defines helper methods for the PyInstaller utility
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import os
import projex

#------------------------------------------------------------------------------

def collect(basepath, exclude=None):
    """
    Collects all the packages associated with the inputed filepath.
    
    :param      module | <module>
    
    :return     ([<str> pkg, ..], [(<str> path, <str> relpath), ..] data)
    """
    if exclude is None:
        exclude = ['.py', '.pyc', '.pyo', '.css', '.exe']
    
    imports = []
    datas = []
    
    # walk the folder structure looking for all packages and data files
    basename = os.path.basename(basepath)
    basepath = os.path.abspath(basepath)
    baselen = len(basepath) - len(basename)
    for root, folders, files in os.walk(basepath):
        if '.svn' in root or '.git' in root:
            continue
        
        # generate the __plugins__.py file
        plugins = None
        if '__plugins__.py' in files:
            plugins = []
        
        if plugins is not None:
            rootpkg = projex.packageFromPath(root)
            
            # include package plugins
            for folder in folders:
                if os.path.exists(os.path.join(root, folder, '__init__.py')):
                    plugins.append('.'.join([rootpkg, folder]))
        
        for file in files:
            module, ext = os.path.splitext(file)
            
            # look for python modules
            if ext == '.py':
                package_path = projex.packageFromPath(os.path.join(root, file))
                if not package_path:
                    continue
                
                if module != '__init__':
                    package_path += '.' + module
                
                imports.append(package_path)
                
                # test to see if this is a plugin file
                if plugins is not None and module not in ('__init__',
                                                          '__plugins__'):
                    plugins.append(package_path)
            
            # look for data
            elif ext not in exclude:
                src  = os.path.join(root, file)
                targ = os.path.join(root[baselen:])
                datas.append((src, targ))
        
        # save the plugin information
        if plugins is not None:
            plugs = ',\n'.join(map(lambda x: "r'{0}'".format(x), plugins))
            data = '__toc__ = [{plugs}]'.format(plugs=plugs)
            fname = os.path.join(root, '__plugins__.py')
            f = open(fname, 'w')
            f.write(data)
            f.close()
    
    return imports, datas


