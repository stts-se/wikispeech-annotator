#!/usr/bin/perl
use strict;
use warnings;

my $VERSION;
$VERSION = '1.02';

# This script converts HTK (http://htk.eng.cam.ac.uk/) format of annotation
# (.lab) file to Praat (http://www.fon.hum.uva.nl/praat/) format of annotation
# (.TextGrid) file.

# See the POD documentation at the end of this file
# or run `perl lab2tg.pl --man'
# for more information.

use Getopt::Long;
use Pod::Usage;

my %opt = (
           help => 0,
           man => 0,
           l1 => 'Level 1',
           l2 => 'Level 2',
           l3 => 'Level 3',
           exclude1 => 0,
           exclude2 => 0,
           exclude3 => 0,
           script => undef,
           ext => 'TextGrid',
           verbose => 0,
           version => 0,
);

GetOptions(\%opt,
           'help|?',
           'man',
           'l1=s',
           'l2=s',
           'l3=s',
           'exclude1|e1',
           'exclude2|e2',
           'exclude3|e3',
           'script|S=s',
           'ext|x=s',
           'verbose|v',
           'version',
) or pod2usage(1);

my %param = (
             maxNumLevels => 5, # max number of transcription levels including
                                # two required time bounds levels
);

pod2usage(1) if $opt{help};
pod2usage(-exitstatus => 0, -verbose => 2) if $opt{man};
print "$VERSION\n" and exit(0) if $opt{version};

if (@ARGV == 0 && !$opt{script}) {
    pod2usage(1);
    exit(0);
}

my $labFileName = '';
my $tgFileName = '';

if (@ARGV > 0) {
    $labFileName = $ARGV[0];
    if (@ARGV > 1) {
        $tgFileName = $ARGV[1];
        if (@ARGV > 2) {
            warn "WARNING: Too many arguments is given to the script.\n";
        }
    }
    else {
        $tgFileName = ChangeFileExt($labFileName, $opt{ext});
    }
    
    print "\nConverting $labFileName -> $tgFileName\n";
    lab2tg($labFileName, $tgFileName);
    print "Done.\n";
}

if ($opt{script}) {
    my $scriptFileName = $opt{script};
    if (-e $scriptFileName) {
        print "\nProcessing $scriptFileName. Please wait...\n";
        my $scriptFile;
        if (!open($scriptFile, "<$scriptFileName")) {
            my $msg = "ERROR: Can't open file $scriptFileName for reading: $!.\n";
            die $msg;
        }
        my $lineNo = 0;
        my $numFiles = 0;
        while (<$scriptFile>) {
            chomp;
            $lineNo++;
            if ($_ !~ /^\s*$/) {        # if current line is not empty, then...
                my @fields = split /\s+/;
                my $labFileName = '';
                my $tgFileName = '';
                if (@fields > 0) {
                    $labFileName = $fields[0];
                    if (@fields > 1) {
                        $tgFileName = $fields[1];
                    }
                    else {
                        $tgFileName = ChangeFileExt($labFileName, $opt{ext});
                    }
                }
                else {
                    my $msg = "Bad format of file $scriptFileName at line $lineNo.\n";
                    die $msg;
                }
                $numFiles++;
                if ($opt{verbose}) {
                    print "$numFiles: Converting $labFileName -> $tgFileName\n";
                }
                lab2tg($labFileName, $tgFileName);
            }
        }
        close($scriptFile);
        print "Done. $numFiles files processed.\n";
    }
    else {
        my $msg = "ERROR: Can't find file $scriptFileName.\n";
        die $msg;
    }
}

sub lab2tg
{
    my $labFileName = shift;
    my $tgFileName = shift;
    
    my @htrans;
    my $numLevels = 0;
    
    if (-e $labFileName) {
        my $labFile;
        if (!open($labFile, "<$labFileName")) {
            my $msg = "ERROR: Can't open file $labFileName for reading: $!.\n";
            die $msg;
        }
        my $lineNo = 0;
        while ( <$labFile> ) {
            $lineNo++;
            chomp;
            if ($_ !~ /^\s*$/) {
                if ($_ =~ /[0-9.]+\s+[0-9.]+\s+.+/) {
                    my @parts = split /\s+/;
                    push @htrans, [ @parts ];
                    if (@parts > $numLevels) {
                        $numLevels = @parts;
                    }
                }
                else {
                    my $msg = "ERROR: Bad syntax in file $labFileName at line $lineNo.\n";
                    die $msg;
                }
            }
        }
        close($labFile);
    }
    else {
        my $msg = "ERROR: Can't find file $labFileName.\n";
        die $msg;
    }
    
    if ($numLevels > $param{maxNumLevels}) {
        my $msg = "ERROR: Number of transcription levels in file $labFileName ";
        $msg .= "exceeds maximum allowed number of transcription levels, which ";
        $msg .= "is equal to ".($param{maxNumLevels}-2).".\n";
        die $msg;
    }
    
    my $tiersSize = $numLevels - 2;
    my $tiersSizeDecrease = 0;
    for my $i ( 0 .. $numLevels-3 ) {
        my $e = "exclude".($i+1);
        if ($opt{$e}) {
            $tiersSizeDecrease++;
        }
    }
    if ($tiersSize <= $tiersSizeDecrease) {
        my $msg = "WARNING: All transcription levels are excluded in ";
        $msg .= "file $labFileName. $labFileName processing aborted.\n";
        warn $msg;
        return;
    }
    
    my $numRows = $#htrans + 1;
    my $globalxmin = $htrans[0][0];
    my $globalxmax = $htrans[$numRows-1][1];
    my @xmin;
    my @xmax;
    my @text;
    
    my $currentLevel = 2;
    
    while ($currentLevel < $numLevels) {
        my $i = 0;
        my $k = 0;
        while ($i < $numRows) {
            # search the begin of phonetic unit
            while ($i < $numRows && !exists($htrans[$i][$currentLevel])) {
                $i++;
            }
            if (exists($htrans[$i][$currentLevel])) {
                # if it is found,
                # remember it and search the end of this phonetic unit
                $xmin[$currentLevel-2][$k] = $htrans[$i][0];
                $text[$currentLevel-2][$k] = $htrans[$i][$currentLevel];
                my $l = $i + 1;
                while ($l < $numRows && !exists($htrans[$l][$currentLevel])) {
                    $l++;
                }
                $xmax[$currentLevel-2][$k] = $htrans[$l-1][1];
                $k++; # increase number of intervals of xmin, xmax 
            }
            $i++;
        }
        $currentLevel++;
    }
    
    my $tgFile;
    if (!open($tgFile, ">$tgFileName")) {
        my $msg = "ERROR: Can't create file $tgFileName: $!.\n";
        die $msg;
    }
    
    $globalxmin *= 1e-07;
    #HB $globalxmax *= 1e-07;
    
    print $tgFile qq(File type = "ooTextFile"\n);
    print $tgFile qq(Object class = "TextGrid"\n\n);
    print $tgFile qq(xmin = $globalxmin\n);
    print $tgFile qq(xmax = $globalxmax\n);
    print $tgFile qq(tiers? <exists>\n);
    my $tiersSize2 = $tiersSize - $tiersSizeDecrease;
    print $tgFile qq(size = $tiersSize2\n);
    print $tgFile qq(item []:\n);
    
    my $itemIndex = 0;
    for my $i ( 0 .. $tiersSize-1 ) {
        my $e = "exclude".($i+1);
        if ($opt{$e}) {
            next;
        }
        $itemIndex++;
        print $tgFile qq(    item [$itemIndex]:\n);
        print $tgFile qq(        class = "IntervalTier"\n);
        my $l = "l$itemIndex";
        print $tgFile qq(        name = "$opt{$l}"\n);
        print $tgFile qq(        xmin = $globalxmin\n);
        print $tgFile qq(        xmax = $globalxmax\n);
        my $intervalsSize = $#{$xmin[$i]} + 1;
        print $tgFile qq(        intervals: size = $intervalsSize\n);
        for my $j ( 0 .. $#{$xmin[$i]} ) {
            my $intervalsIndex = $j + 1;
            print $tgFile qq(        intervals [$intervalsIndex]:\n);
	    #HB
            #$xmin[$i][$j] *= 1e-07;
            #$xmax[$i][$j] *= 1e-07;
            print $tgFile qq(            xmin = $xmin[$i][$j]\n);
            print $tgFile qq(            xmax = $xmax[$i][$j]\n);
            print $tgFile qq(            text = "$text[$i][$j]"\n);
        }
    }
    close($tgFile);
}

sub ChangeFileExt
{
    my $fileName = shift;
    my $ext = shift;
    
    if ($fileName =~ s/\.[\w\ ]*$/\.$ext/) {
    }
    else {
        $fileName = $fileName.'.'.$ext;
    }
    return $fileName;
}

__END__

=head1 NAME

lab2tg.pl - convert HTK (http://htk.eng.cam.ac.uk/) format of annotation (.lab)
file to Praat (http://www.fon.hum.uva.nl/praat/) format of annotation
(.TextGrid) file.

=head1 SYNOPSIS

=over

=item B<lab2tg.pl> [I<options>] I<labFile> [I<textGridFile>]

=item B<lab2tg.pl> [I<options>] I<--script f> [I<labFile>] [I<textGridFile>]

=back

=head1 DESCRIPTION

Converts HTK (http://htk.eng.cam.ac.uk/) format of annotation (.lab) file
I<labFile> to Praat (http://www.fon.hum.uva.nl/praat/) format of annotation
(.TextGrid) file I<textGridFile>. If I<textGridFile> (output) file name is not
provided, I<labFile> (source) file name will be used instead, but with different
extension (C<.TextGrid> by default). The script file I<f> can be used for batch
conversion of multiple files. In this case, a list of each source file and
(optional) its corresponding output file should be provided in the script file.

=head1 OPTIONS

=over

=item B<--l1> I<l>

Set label I<l> for the 1st level of transcriptions. The default is C<Level 1>.

=item B<--l2> I<l>

Set label I<l> for the 2nd level of transcriptions. The default is C<Level 2>.

=item B<--l3> I<l>

Set label I<l> for the 3rd level of transcriptions. The default is C<Level 3>.

=item B<-e1>, B<--exclude1>

Exclude the 1st level of transcriptions. The default is off.

=item B<-e2>, B<--exclude2>

Exclude the 2nd level of transcriptions. The default is off.

=item B<-e3>, B<--exclude3>

Exclude the 3rd level of transcriptions. The default is off.

=item B<-S> I<f>, B<--script> I<f>

Set script file to I<f>. The script file can be used for batch conversion of
multiple files. In this case, a list of each source file and (optional) its
corresponding output file should be provided in the script file. The default is
none.

=item B<-x> I<ext>, B<--ext> I<ext>

Set default TextGrid output file extension to I<ext>. The default is
C<.TextGrid>.

=item B<-v>, B<--verbose>

Verbose output to the screen. The default is off.

=item B<-?>, B<--help>

Prints the B<SYNOPSIS> and B<OPTIONS> sections.

=item B<--man>

Prints the lab2tg.pl manual.

=item B<--version>

Prints the current version number of lab2tg.pl and exits.

=back

=head1 HISTORY

v1.02 (20080922):
  Minor updates of POD documentation.

v1.01 (20080917):
  Minor updates of POD documentation.

v1.00 (20080916):
  Initial public release.

=head1 AUTHOR

Mark Filipovic <F<markfi@cpan.org>>

=head1 COPYRIGHT

  Copyright (c) 2008 Mark Filipovic.  All rights reserved.
  This program is free software; you can redistribute it and/or modify it
  under the same terms as Perl itself.

=begin CPAN

=head1 README

This script converts HTK (http://htk.eng.cam.ac.uk/) format of annotation (.lab)
file to Praat (http://www.fon.hum.uva.nl/praat/) format of annotation
(.TextGrid) file.

=head1 PREREQUISITES

This script requires C<strict>, C<warnings>, C<Getopt::Long>, and C<Pod::Usage>
modules.

=head1 OSNAMES

any

=head1 SCRIPT CATEGORIES

Speech/Recognition
Speech/Processing

=end CPAN

=cut
