#!/usr/bin/python
#
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is used to validate that the library is correct.

This checks:
 * All files in lib/ appear when compiling +@complete
 * Runs a compiler pass over the test code to check for type errors"""

import build
import os
import re
import shakaBuildHelpers
import sys

def checkComplete():
  """Checks whether the 'complete' build references every file.  This is used
  by the build script to ensure that every file is included in at least one
  build type.

  Returns:
    True on success, False on failure.
  """
  complete = build.Build()
  # Normally we don't need to include @core, but because we look at the build
  # object directly, we need to include it here.  When using main(), it will
  # call addCore which will ensure core is included.
  if not complete.parseBuild(['+@complete', '+@core'], os.getcwd()):
    print >> sys.stderr, 'Error parsing complete build'
    return False

  match = re.compile(r'.*\.js$')
  base = shakaBuildHelpers.getSourceBase()
  allFiles = shakaBuildHelpers.getAllFiles(os.path.join(base, 'lib'), match)
  missingFiles = set(allFiles) - complete.include

  if len(missingFiles) > 0:
    print >> sys.stderr, 'There are files missing from the complete build:'
    for missing in missingFiles:
      # Convert to a path relative to source base.
      print >> sys.stderr, '  ' + os.path.relpath(missing, base)
    return False
  return True

def checkTests():
  """Runs an extra compile pass over the test code to check for type errors.

  Returns:
    True on success, False on failure.
  """
  match = re.compile(r'.*\.js$')
  base = shakaBuildHelpers.getSourceBase()
  def get(*args):
    return shakaBuildHelpers.getAllFiles(os.path.join(base, *args), match)
  files = (get('lib') + get('externs') + get('test') +
      get('third_party', 'closure'))
  testBuild = build.Build(set(files))

  # Ignore missing goog.require since we assume the whole library is
  # already included.
  opts = ['--jscomp_off=missingRequire', '--checks-only', '-O', 'SIMPLE']
  return testBuild.buildRaw(opts)

def usage():
  print 'Usage:', sys.argv[0]
  print
  print __doc__

def main(args):
  for arg in args:
    if arg == '--help':
      usage()
      return 0
    else:
      print >> sys.stderr, 'Unknown option', arg
      usage()
      return 1
  if not checkComplete():
    return 1
  elif not checkTests():
    return 1
  else:
    return 0

if __name__ == '__main__':
  shakaBuildHelpers.runMain(main)

