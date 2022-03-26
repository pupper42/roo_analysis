# Before `make install' is performed this script should be runnable with
# `make test'. After `make install' it should work as `perl test.pl'

######################### We start with some black magic to print on failure.

# Change 1..1 below to 1..last_test_to_print .
# (It may become useful if the test is moved to ./t subdirectory.)

BEGIN { $| = 1; print "1..7\n"; }
END {print "not ok 1\n" unless $loaded;}
use PDL;
use SP3;
$loaded = 1;
print "ok 1\n";

######################### End of black magic.

# Insert your test code below (better if it prints "ok 13"
# (correspondingly "not ok 13") depending on the success of chunk 13
# of the test code):

# GPS orbits

$infile = "test_gps_orb.sp3";
$outfile = "test_out.sp3";

BEGIN { if (-e $outfile) { print "removing test output file:  $outfile\n"; unlink $outfile; }}
#END { print "removing test output file:  $outfile\n"; unlink $outfile; }

eval { ($times, $pos, $options, $vel) = SP3::readSP3 ($infile); };
if (!$@) {
  print "ok 2\n";
} else {
  print "not ok 2\n";
}

eval { SP3::writeSP3 ($outfile, $times, $pos, $options, $vel); };
if (!$@) {
  print "ok 3\n";
} else {
  print "not ok 3\n";
}

$diffs = `diff $infile $outfile 2>&1`;
if ($diffs eq '') {
  print "ok 4\n";
} else {
  print "not ok 4\n";
}


# LEO orbits

$infile = "test_leo_orb.sp3";
$outfile = "test_out.sp3";

eval { ($times, $pos, $options, $vel) = SP3::readSP3 ($infile); };
if (!$@) {
  print "ok 5\n";
} else {
  print "not ok 5\n";
}

$options->{SATIDS} = [901];  # give mapping.  Index zero in $pos, $vel
                             # is sat id 901 for output file.

eval { SP3::writeSP3 ($outfile, $times, $pos, $options, $vel); };
if (!$@) {
  print "ok 6\n";
} else {
  print "not ok 6\n";
}

$diffs = `diff $infile $outfile 2>&1`;
if ($diffs eq '') {
  print "ok 7\n";
} else {
  print "not ok 7\n";
}

