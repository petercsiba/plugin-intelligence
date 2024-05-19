import Container from '@mui/material/Container';
import MarketplaceCompanies from "../MarketplaceCompanies";
import {MarketplaceName} from "../models";
import MarketplacePlugins from "../MarketplacePlugins";
import PageTitle from "@/components/PageTitle";
import SubPageTitle from "@/components/SubPageTitle";
import MarketplaceStats from "../MarketplaceStats";
import { Box } from '@mui/material';



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
                <MarketplaceStats marketplaceName={MarketplaceName.GOOGLE_WORKSPACE} />

                {/*For instance, since 2017, Atlassian&apos;s Trello integration with Gmail has garnered over 7 million installs,*/}
                {/*demonstrating the potential reach and impact of well-developed integrations.*/}
                <SubPageTitle title={"Distribution of Add Ons by Downloads"} />
                <Box
                component="img"
                src="/charts/google-workspace-histogram-user-count.png"
                alt="Histogram of Download Ranges for Google Workspace"
                sx={{ height: 300 }}
                />
            </Container>
            <MarketplaceCompanies marketplaceName={MarketplaceName.GOOGLE_WORKSPACE} />
            <MarketplacePlugins marketplaceName={MarketplaceName.GOOGLE_WORKSPACE} />
        </Container>
    );
}
