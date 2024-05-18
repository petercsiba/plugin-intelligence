import React from 'react';
import Container from '@mui/material/Container';
import MarketplaceCompanies from "../MarketplaceCompanies";
import { MarketplaceName } from "../models";
import MarketplacePlugins from "../MarketplacePlugins";
import PageTitle from "@/components/PageTitle";
import SubPageTitle from "@/components/SubPageTitle";

export default function GoogleWorkspace() {
    return (
        <Container maxWidth="lg">
            <PageTitle title="Google Workspace Marketplace Overview" />
            <Container maxWidth="sm">
                The Google Workspace Marketplace, launched on March 10, 2010 (as Google Apps),
                revolutionizes how administrators discover, purchase, and deploy integrated third-party
                cloud applications to their domains.

                These applications seamlessly integrate with Gmail, Google Docs, Sheets and other Google Apps using open protocols.
                <SubPageTitle title={"Key Facts and Figures"} />
                {/*TODO: Get this from the DB*/}
                <ul>
                    <li><strong>Number of Public Apps</strong>: Over 5,300</li>
                    <li><strong>Total Downloads:</strong> Over 4.8 billion</li>
                    <li><strong>Google Workspace Unique Users</strong>: More than 3 billion</li>
                </ul>

                For instance, since 2017, Atlassian&apos;s Trello integration with Gmail has garnered over 7 million installs,
                demonstrating the potential reach and impact of well-developed integrations.
            </Container>
            <MarketplaceCompanies marketplaceName={MarketplaceName.GOOGLE_WORKSPACE} />
            <MarketplacePlugins marketplaceName={MarketplaceName.GOOGLE_WORKSPACE} />
        </Container>
    );
}
