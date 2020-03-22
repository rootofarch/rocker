
import argparse

from .core import DockerImageGenerator
from .core import get_rocker_version
from .core import list_plugins


def main():

    parser = argparse.ArgumentParser(description='A tool for building and testing gh-pages locally')
    parser.add_argument('directory')
    #parser.add_argument('command', nargs='*', default='')
    parser.add_argument('--nocache', action='store_true',
        help='Force a rebuild of the image')
    # TODO(tfoote) add prebuilt images for faster operations 
    # parser.add_argument('--develop', action='store_true',
    #    help='Build the image locally not using the prebuilt image.')
    parser.add_argument('--port', type=int, action='store', default='4000')
    parser.add_argument('--baseurl', type=str, action='store', default=None)
    parser.add_argument('-v', '--version', action='version',
        version='%(prog)s ' + get_rocker_version())
    parser.add_argument('--build-only', action='store_true')
    # TODO(tfoote) add verbose parser.add_argument('--verbose', action='store_true')


    plugins = list_plugins()
    for p in plugins.values():
        p.register_arguments(parser)

    args = parser.parse_args()
    args_dict = vars(args)
    args_dict['directory'] = os.path.abspath(args_dict['directory'])

    if args.build_only and args.baseurl:
        parser.error("build and baseurl options are incompatible")


    if args.build_only:
        args_dict['command'] = 'jekyll build -V --trace'
    else:
        args_dict['command'] = 'jekyll serve -w'
        if args.baseurl is not None:
            # Don't output to the default location if generating using a modified baseurl
            args_dict['command'] += ' --baseurl=\'{baseurl}\' -d /tmp/aliased_site'.format(**args_dict)
    plugins = list_plugins()
    required_plugins = ['ghpages', 'user']
    gh_pages = [e() for e in plugins.values() if e.get_name() in required_plugins]
    dig = DockerImageGenerator(gh_pages, args_dict, 'ubuntu:bionic')

    exit_code = dig.build(**vars(args))
    if exit_code != 0:
        print("Build failed exiting")
        return exit_code

    return dig.run(**args_dict)