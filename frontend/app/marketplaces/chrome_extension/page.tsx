import React from 'react';
import Container from '@mui/material/Container';
import MarketplaceCompanies from "../MarketplaceCompanies";
import {MarketplaceName} from "../models";
import MarketplacePlugins from "../MarketplacePlugins";
import PageTitle from "@/components/PageTitle";
import SubPageTitle from "@/components/SubPageTitle";
import { Box } from '@mui/material';
import MarketplaceStats from "../MarketplaceStats";

export default function ChromeExtensions() {
    return (
        <Container maxWidth="lg">
            <PageTitle title="Chrome Extensions Web Store Overview" />
            <Container maxWidth="sm">
                The Chrome Web Store, launched on December 6, 2010,
                has transformed the way users discover and install browser extensions for Google Chrome.

                These extensions enhance the functionality of the Chrome browser by integrating
                with various web services and providing additional features.

                <SubPageTitle title={"Key Facts and Figures"} />
                <MarketplaceStats marketplaceName={MarketplaceName.CHROME_EXTENSION} />

                {/*For example, Adblock Plus, one of the most popular Chrome extensions, has been installed over 100 million times, showcasing the significant reach and impact of high-quality extensions.*/}


                <SubPageTitle title={"Distribution of Extensions by User Count"} />
              <Box
                component="img"
                src="/charts/chrome-extension-histogram-user-count.png"
                alt="Histogram of User Count Ranges for Chrome Extensions"
                sx={{ height: 300 }}
              />
            </Container>
            <MarketplaceCompanies marketplaceName={MarketplaceName.CHROME_EXTENSION} />
            <MarketplacePlugins marketplaceName={MarketplaceName.CHROME_EXTENSION} />
        </Container>
    );
}
