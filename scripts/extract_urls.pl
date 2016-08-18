#!/usr/bin/perl
# 
# Extract the URIs from an RDF file that match a given topic.
#
use strict;
use warnings;

my $file; 
my @urls;
my $url;
my $have_topic = 0;

if ($#ARGV != 0) {
    print "\nUsage: extract_urls filename\n";
    exit;
}

$file = $ARGV[0];

open(my $fh, "<", $file) or die "Unable to open $file\n";

while (my $line = <$fh>) {
    if ($line =~ m/Topic r:id="Top\/World\/Chinese_Simplified/) {
        $have_topic = 1;
    }
    if ($have_topic) {
        if ($line =~ m/<(?:ExternalPage about|link r:resource)="([^\"]+)"\/?>/) {
            push @urls, $1;
        } elsif ($line =~ m/\/Topic>/) {
            $have_topic = 0;
        }
    } 
}

close $fh;

foreach $url (@urls) {
    print $url;
    print "\n";
}
