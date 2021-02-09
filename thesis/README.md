Master thesis "Uncovering Fingerprinting Networks. An Analysis of In-Browser Tracking using a Behavior-based Approach"
==========================================================================

This repository contains the master thesis written by Sebastian Neef at the chair of "Security in Telecommunication" at the Technische Universität Berlin in 2021. The thesis was supervised by Jean-Pierre Seifert and assistant supervisor Julian Fietkau.

Furthermore, this repository includes the fingerprinting networks scanner "FPNET" and the related analysis tools.

## Abstract

Throughout recent years, the importance of internet-privacy has continuously risen. The General Data Protection Regulation by the European Union fundamentally changed digital data processing by requiring explicit consent for processing personally identifiable information. In combination with the cookie law, users can opt-out of being profiled by advertisers or other entities. Browser fingerprinting is a technique that does not require cookies or persistent identifiers. It derives a sufficiently unique identifier from the various browser or device properties. Academic work has covered offensive and defensive fingerprinting methods for almost a decade, observing a rise in popularity. 


This thesis explores the current state of browser fingerprinting on the internet. For that, we implement FPNET~- a scalable & reliable tool based on FPMON, to identify fingerprinting scripts on large sets of websites by observing their behavior. By scanning the Alexa Top 10,000 websites, we spot several hundred networks of equally behaving scripts. For each network, we determine the actor behind it. We track down companies like Google, Yandex, Maxmind, Sift, or FingerprintJS, to name a few. 

In three complementary studies, we further investigate the uncovered networks with regards to I) randomization of filenames or domains, II) behavior changes, III) security. Two consecutive scans reveal that only less than 12.5% of the pages do not change script files. With our behavior-based approach, we successfully re-identify almost 9,000 scripts whose filename or domain changed, and over 86% of the scripts without URL changes. The security analysis shows an adoption of TLS/SSL to over 98% and specific web security headers set for over 30% of the scripts.

Finally, we voice concerns about the unavoidability of modern fingerprinting and its implications for internet users' privacy since we believe that many users are unaware of being fingerprinted or have insufficient possibilities to protect against it.