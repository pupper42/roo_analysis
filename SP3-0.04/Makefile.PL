# Makefile.PL for PDL::IO::SP3 module.

use ExtUtils::MakeMaker;

WriteMakefile(
	      'NAME'  	=> 'SP3',
	      'VERSION_FROM'  => 'SP3.pm',

# Special for COSMIC (delete for normal installation under perl5 lib dir)
#	      'INSTALLSITELIB'=> '/ops/tools/lib',  
#	      'INSTALLBIN'    => '/ops/tools/bin',  
#	      'INSTALLMAN3DIR'=> '/ops/tools/man/man3', 
#	      'INSTALLMAN1DIR'=> '/ops/tools/man/man1', 

);
