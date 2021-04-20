These demo applications have been built on Ubuntu Linux version
16.04.2 LTS (xenial), using GCC version 5.4.0, for a
64-bit (x86) architecture.

The only demo application not available for Linux is the powerful
"kdu_show" app, which is available only on Windows and Mac platforms.

To use these demo executables, you will need to edit your ".profile"
file to add the current directory to your executable PATH variable
and also to the LD_LIBRARY_PATH variable.  Below is an example of
how this might be done for the typical BASH shell.

PATH=$PATH:~/kakadu/bin
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/kakadu/bin
export PATH
export LD_LIBRARY_PATH

In some versions of Ubuntu, you may find that the LD_LIBRARY_PATH
export gets overwritten when gnome starts, in which case you can
move the above definitions to ".bashrc" and all will be well.

Terms and Conditions:

The Kakadu demonstration applications may be used for strictly non-commercial purposes only.  For information on licensing Kakadu, please visit www.kakadusoftware.com.

You shall not hold liable the author, David Taubman, the copyright holder, UNSW Innovations Pty Ltd, or the University of New South Wales, for any financial loss or other damage resulting from the use of these demonstration applications.
