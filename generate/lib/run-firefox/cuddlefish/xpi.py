import os
import zipfile
import simplejson as json
from cuddlefish.util import filter_filenames, filter_dirnames

def build_xpi(template_root_dir, manifest, xpi_name,
              harness_options, limit_to=None):
    zf = zipfile.ZipFile(xpi_name, "w", zipfile.ZIP_DEFLATED)

    open('.install.rdf', 'w').write(str(manifest))
    zf.write('.install.rdf', 'install.rdf')
    os.remove('.install.rdf')

    if 'icon' in harness_options:
        zf.write(str(harness_options['icon']), 'icon.png')
        del harness_options['icon']

    if 'icon64' in harness_options:
        zf.write(str(harness_options['icon64']), 'icon64.png')
        del harness_options['icon64']

    IGNORED_FILES = [".hgignore", ".DS_Store", "install.rdf",
                     "application.ini", xpi_name]

    for dirpath, dirnames, filenames in os.walk(template_root_dir):
        filenames = list(filter_filenames(filenames, IGNORED_FILES))
        dirnames[:] = filter_dirnames(dirnames)
        for filename in filenames:
            abspath = os.path.join(dirpath, filename)
            arcpath = abspath[len(template_root_dir)+1:]
            zf.write(abspath, arcpath)

    new_resources = {}
    for resource in harness_options['resources']:
        base_arcpath = os.path.join('resources', resource)
        new_resources[resource] = ['resources', resource]
        abs_dirname = harness_options['resources'][resource]
        # Always write the directory, even if it contains no files,
        # since the harness will try to access it.
        dirinfo = zipfile.ZipInfo(base_arcpath + "/")
        dirinfo.external_attr = 0755 << 16L
        zf.writestr(dirinfo, "")
        for dirpath, dirnames, filenames in os.walk(abs_dirname):
            goodfiles = list(filter_filenames(filenames, IGNORED_FILES))
            for filename in goodfiles:
                abspath = os.path.join(dirpath, filename)
                if limit_to is not None and abspath not in limit_to:
                    continue
                arcpath = abspath[len(abs_dirname)+1:]
                arcpath = os.path.join(base_arcpath, arcpath)
                zf.write(str(abspath), str(arcpath))
            dirnames[:] = filter_dirnames(dirnames)
    harness_options['resources'] = new_resources

    open('.options.json', 'w').write(json.dumps(harness_options, indent=1,
                                                sort_keys=True))
    zf.write('.options.json', 'harness-options.json')
    os.remove('.options.json')

    zf.close()
