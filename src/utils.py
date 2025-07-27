import pip

def install(package):
    try:
        import ucimlrepo
    except:
        pip.main(["install",package])