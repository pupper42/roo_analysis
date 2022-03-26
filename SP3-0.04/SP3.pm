#/**----------------------------------------------------------------------    
# @name       SP3.pm
# Read and write SP3 (Standard Product 3) orbit files from/to perl/PDL objects.
#
# @author     Doug Hunt
# @since      01/31/2000
# @version    $Revision$
# -----------------------------------------------------------------------*/

package SP3;

$VERSION = '0.04';

use PDL;
use Exporter;
use TimeClass;

@SP3::ISA = qw/Exporter/;

@EXPORT = qw(readSP3 writeSP3);

$SP3::err = -999;  # error/missing value number.

#/**----------------------------------------------------------------------    
# @name       readSP3
# 
# Read in data from a LEO SP3 file containing one satellites worth of 
# position and velocity data.
# 
# @parameter  infile   The name of the file to read
# @return     1) PDL of times for pos/vel values, in GPS seconds
# @           2) 3D PDL (time step, XYZ, sat ID) of position values matching above times (km)
# @           3) 3D PDL (time step, XYZ. sat ID) of velocity values matching above times (km/sec)
# @           4) ref to hash of values read from header with info on file.
# ----------------------------------------------------------------------*/
sub readSP3 {

  my $infile = shift;
  
  open (IN, $infile) or die "Cannot open file:  $infile";

  #
  ## Unpack header
  #
  my ($pv, $yr, $mo, $day, $hr, $min, $sec, $nrec, $coordsys, $orbtype, $agency) = 
    unpack ("x2 a a4 x a2 x a2 x a2 x a2 x a11 x a7 x7 a5 x a3 x a4", <IN>);

  my %options = ('COORDSYS' => $coordsys,
		 'ORBTYPE'  => $orbtype,
		 'AGENCY'   => $agency);

  my ($gpswk, $gpswksec, $interval) = 
    unpack ("x3 a4 x a15 x a14", <IN>);

  my ($nsats, @satids) = 
    unpack ("x4 a2 x3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3", <IN>);
  for (my $i=0;$i<4;$i++) {
    push (@satids, 
	  unpack ("x9 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3 a3", <IN>));
  }
  @satids = @satids[0..$nsats-1];

  for (my $i=0;$i<15;$i++) { <IN>; } # read past some stuff

  #
  ## Pre-allocate hashes of PDLs for position and velocity.  Fill in with error values.
  #
  
  # The pdl sat dim is either: 1 for single satellite input files or
  # the max sat id plus one for multiple satellite files.
  # This works well for GPS orbits with sat ids from 1 to 31
  # and LEO files with one sat id in the hundreds.  This
  # would break down if there were two satellites with large sat ids in the
  # input file.  This would cause very sparse output PDLs!
  my $satdim = ($nsats == 1) ? 1 : max(pdl(@satids)) + 1;  
  my $time = zeroes($nrec) + $SP3::err;
  my $pos  = zeroes($nrec,3,$satdim) + $SP3::err;
  
  my $vel;
  my $nvals = 1;
  if ($pv eq 'V') {
    $vel = zeroes($nrec,3,$satdim) + $SP3::err;
    $nvals = 2;
  }

  use integer; # an attempt to speed this loop up...
  for (my $i=0;$i<$nrec;$i++) {

    # skip read in epoch time
    <IN>;
    my $gpssec  = ($gpswk * 604800) + $gpswksec + ($i * $interval);
   
    PDL::Core::set_c ($time, [$i], $gpssec); # use Core::set_c instead of 'set' to speed things up...

    # read in positions [and velocities]
    for (my $j=0;$j<$nvals*$nsats;$j++) {
      my ($f, $id, $x, $y, $z) = unpack ("a a3 a14 a14 a14", <IN>);
      if ($nsats == 1) { $id = 0; }
      # print "j = $j, f = $f, id = $id\n";
      if ($f eq 'P') {
	PDL::Core::set_c ($pos, [$i, 0, $id], $x); 
	PDL::Core::set_c ($pos, [$i, 1, $id], $y); 
	PDL::Core::set_c ($pos, [$i, 2, $id], $z);
      } elsif ($f eq 'V') {
	PDL::Core::set_c ($vel, [$i, 0, $id], $x); 
	PDL::Core::set_c ($vel, [$i, 1, $id], $y); 
	PDL::Core::set_c ($vel, [$i, 2, $id], $z);
      } else {
	die "Illegal type flag $f at record $i in $infile";
      }
    }

  }

  close (IN);

  if (defined($vel)) {
    return ($time, $pos, \%options, $vel);
  } else {
    return ($time, $pos, \%options);
  }

}


#/**----------------------------------------------------------------------    
# @name       writeSP3
# 
# Write out an SP3 file
# 
# @parameter  sp3file -- The name of the file to write
# @           times   -- PDL of times for pos/vel values, in GPS seconds
# @           pos     -- 3D PDL (time step, XYZ, sat ID) of position values matching 
# @                      above times (km)
# @           vel     -- 3D PDL (time step, XYZ, sat ID) of velocity values matching 
# @                      above times (km/sec) (optional)
# @           $options-- ref to hash of optional header values for the output file.
# @return     file written or exception thrown.           
# ----------------------------------------------------------------------*/
sub writeSP3 {
  my $sp3file = shift;
  my $times   = shift;
  my $pos     = shift;
  my $options = shift;
  my $vel     = shift;

  my $pv = 'P';
  if (defined($vel)) {
    $pv = 'V';  # position only or position and velocity
  }

  # Determine the number and ids of satellites from the input PDLs
  my @satids;

  # if satids specified as option use this
  if (exists ($options->{'SATIDS'})) {
    @satids = @{$options->{'SATIDS'}};

    # Otherwise, the index of all non-error position values are the sat ids
    # IE if index numbers 1, 3, 6, 15 of the $pos vector have good values, the
    # ids of the satellites are 1, 3, 6 and 15 (this is convenient for GPS satellite SVNs).
  } else {
    my $satvec = $pos->slice ("(0),(0),:");
    @satids = list which ($satvec != $SP3::err);
  }
      
  my $nsats = @satids;

  # Fill @id out to 85 entries
  push (@satids, (0) x (85 - @satids));

  # determine misc header fields
  $coordsys = $options->{'COORDSYS'} || '?????';
  $orbtype  = $options->{'ORBTYPE'}  || '???';
  $agency   = $options->{'AGENCY'}   || '????';

  # Set up and write header
  open (SP3, ">$sp3file");
  my $timec = TimeClass->new->set_gps($times->at(0));

  my ($yr, $mo, $day, $hr, $min, $sec, $nrec, $gpswk, $gpswkday,
      $gpswksec, $interval, $mjd, $fracday);

  ($yr, $mo, $day, $hr, $min, $sec) = $timec->get_gps_breakdown();
  $nrec = $times->nelem;
  ($gpswk, $gpswkday) = $timec->get_gpsweek_day();
  $gpswksec = $times->at(0) - ($gpswk * 604800);
  $interval = $times->at(1) - $times->at(0);
  $mjd = $timec->get_mjd();
  $fracday = $mjd - int($mjd);
  $mjd = int($mjd);

  # write header
  write SP3;

  for (my $i=0;$i<$times->nelem;$i++) {
    ($yr, $mo, $day, $hr, $min, $sec) = $timec->set_gps($times->at($i))->get_gps_breakdown;
    printf SP3 ("*  %04d %2d %2d %2d %2d %11.8f\n", $yr, $mo, $day, $hr, $min, $sec);
    for (my $j=0;$j<$nsats;$j++) {
      my $id  = $satids[$j];
      my $idx = ($nsats == 1) ? 0 : $id;
      printf SP3 ("P%3d%14.6f%14.6f%14.6f 999999.9999\n", 
		  $id, $pos->at($i,0,$idx), $pos->at($i,1,$idx), $pos->at($i,2,$idx));
      printf SP3 ("V%3d%14.6f%14.6f%14.6f 999999.9999\n", 
		  $id, $vel->at($i,0,$idx), $vel->at($i,1,$idx), $vel->at($i,2,$idx)) if (defined($vel));
    }
  }
  print SP3 "EOF\n";
  close SP3;
  return;

  # define format for header
format SP3 =
@a@@>>> @> @> @> @> @#.######## @>>>>>>       @<<<< @<< @<<<
'#', $pv, $yr, $mo, $day, $hr, $min, $sec, $nrec, $coordsys, $orbtype, $agency
@> @>>> @#####.######## @####.######## @>>>> @.#############
'##', $gpswk, $gpswksec,      $interval,     $mjd, $fracday
+   @>   @>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>
$nsats, @satids[0..16]
+        @>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>
@satids[17..33]
+        @>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>
@satids[34..50]
+        @>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>
@satids[51..67]
+        @>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>@>>
@satids[68..84]
++         0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
++         0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
++         0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
++         0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
++         0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
%c cc cc ccc ccc cccc cccc cccc cccc ccccc ccccc ccccc ccccc
%c cc cc ccc ccc cccc cccc cccc cccc ccccc ccccc ccccc ccccc
%f 00.0000000 00.000000000 00.00000000000 00.000000000000000
%f 00.0000000 00.000000000 00.00000000000 00.000000000000000
%i 0000 0000 0000 0000 000000 000000 000000 000000 000000000
%i 0000 0000 0000 0000 000000 000000 000000 000000 000000000
/* CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
/* CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
/* CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
/* CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
.

}


=head1 NAME

SP3 -- Read and Write NOAA/NGS SP3 (Standard Product 3) orbit description files to/from perl/PDL objects.

=head1 SYNOPSIS

	use PDL;
	use SP3;

        ($times,$pos,[$vel]) = readSP3("filename");
        writeSP3 ("filename", $times, $pos, [$vel], [options_hash]);

=head1 DESCRIPTION

This package gives quick, basic access to these orbit description files
(described fully at:  http://www.ngs.noaa.gov/GPS/SP3_format.html).

=head1 FUNCTIONS

=head2 readSP3

=for ref

Read time, position and optionally velocity into PDL objects from
an input SP3 file.

=for usage

 ($times, $pos, $options, [$vel]) = readSP3("filename");

Currently the $options hash returned contains these values:

 $options->{COORDSYS}   The coordinate system used, ex:  ITR94.
 $options->{ORBTYPE}    The type of orbit, ex:  FIT
 $options->{AGENCY}     The agency which generated these orbits, ex:  NOAA

=head2 writeSP3

=for ref

Write an SP3 file from input time, position and optional velocity
PDLs.  Also takes an optional options hash which specifies details about
the input positions and velocities to be put in the header.

=for usage

  writeSP3 ("filename", $times, $pos, [$options], [$vel]);

The $options hash can contain any of the above values, plus the 
following:

  $options->{SATIDS}    A reference to a perl list which contains
                        the mapping between the position in the
                        input pos/vel arrays and the satellite number(s)
                        For example, $options->{SATIDS} = [901, 311] means
                        that the satellite at index 0 has id 901 and
                        that satellite at index 1 has id 311. This
                        id is written to the output file.

=head1 AUTHOR

Copyright (C) Doug Hunt <dhunt@ucar.edu> 
and the University Corporation for Atmospheric Research 2000.
All rights reserved. There is no warranty.
Terms are that of the perl 'Artistic License'.
Redistribution allowed as long as this copyright notice is kept.

=cut
