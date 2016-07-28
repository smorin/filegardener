import io
import os
import invoke


@invoke.task
def testdirs(ctx):
    """
    Lists all the directories in test_data in a file DIRECTORIES.txt
    """
    print("[generate.testdirs] Generating DIRECTORIES.txt")

    with io.open("test_data/DIRECTORIES.txt", "w", encoding="utf8") as fp:
        for dirpath, dirnames, files in os.walk('test_data'):
            fp.write(unicode(dirpath))
            fp.write(u"\n")


