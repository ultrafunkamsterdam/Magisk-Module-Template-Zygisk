import os
import pathlib
import sys
import shutil
import select
import traceback


def get_appdata_path():
    home = pathlib.Path.home()
    if sys.platform.startswith('win32'):
        return os.environ.get('LOCALAPPDATA',
            os.path.join(str(home), "APPDATA", "LOCAL"))
    elif sys.platform.startswith("linux"):
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"

def find_ndk():
    candidates = {}
    sdk = os.path.join(get_appdata_path(), "Android", "Sdk")
    if os.path.exists(sdk):
        ndk = os.path.join(sdk, "ndk")
    if os.path.exists(ndk):
        versions = os.listdir(ndk)
        for v in versions:
            ndk_root = os.path.join(ndk, str(v))
            is_active = not os.path.exists(os.path.join(ndk_root, '.installer'))
            if is_active:
                candidates[v] = ndk_root
        return candidates

def clean(project_path=os.path.join('src', 'zygisk','module')):
    shutil.rmtree(os.path.join(project_path, 'obj'))
    shutil.rmtree(os.path.join(project_path, 'libs'))
    shutil.rmtree(os.path.join(project_path, 'build'))


def build(project_path, use_low=False):
    candidates = find_ndk()
    import subprocess
    menu = []
    for candidate in candidates:
        build_script = 'ndk-build.cmd' if sys.platform.startswith('win32') else 'ndk-build.sh'
        build_script = os.path.join(
            candidates[candidate],
            build_script)
        menu.append(build_script)

    for i,item in enumerate(menu):
        print(f'{i} {item}')

    print(
        'make a hoice by tying in which version you would like to use. '
        'proceeds automatically with higest version after 10 seconds'
    )
    i, o, e = select.select( [sys.stdin], [], [], 10 )
    if(i):
        print('choice confirmed')
        choice = menu[i]
    else:
        choice = menu[len(menu)-1]

    print('_____________ BUILDING USING ', choice, '________________________')
    try:
        sp = subprocess.run([choice, '-C', project_path], shell=True, check=True)
    except (subprocess.CalledProcessError,FileNotFoundError):
        traceback.print_exc()    
    libs_dir = os.path.join(project_path, 'libs')
    for arch in os.listdir(libs_dir):
        fp = os.path.join(libs_dir, arch)
        for file in os.listdir(fp):
            libfp = os.path.join(fp, file)
            shutil.copyfile(libfp, f'magisk\\zygisk\\{arch}.so')
    shutil.make_archive('module', 'zip', 'magisk')


import argparse
parser = argparse.ArgumentParser(prog='build script', 
                                 epilog=f'examples:\n\n .{os.sep}{sys.argv[0]} build \n .{os.sep}{sys.argv[0]} clean',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.set_defaults(build=False, clean=False)

subparsers = parser.add_subparsers()
subparser1 = subparsers.add_parser('build', help="bong3")
subparser2 = subparsers.add_parser('clean', help="bong2")
subparser3 = subparsers.add_parser('oldest', help="bong1")

subparser1.set_defaults(build=True)
subparser2.set_defaults(clean=True)
subparser3.set_defaults(oldest=True)

args = parser.parse_args()

if __name__ == '__main__':

    print(args)
    exit()
    # if no command is set, assume we need to build
    use_low = False
    if not args.clean ^ args.build:
        args.build = True
    if args.low:
        use_low = True
    if args.clean:
        print(clean('src/zygisk/module'))

    if args.build:
        print(build('src/zygisk/module', use_low=True))