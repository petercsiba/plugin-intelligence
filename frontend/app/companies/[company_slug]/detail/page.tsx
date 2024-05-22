import React from "react";
import {
    Container,
    Paper,
    Typography,
    List,
    ListItem,
    ListItemText,
} from "@mui/material";
import Box from "@mui/material/Box";
import ExternalLink from "@/components/ExternalLink";
import dynamic from "next/dynamic";
import {fetchCompanyDetails} from "../../driver";
import NoResultsFound from "@/components/NoResultsFound";
import {formatNumberShort } from "@/utils";
import PluginTable from "../../../plugins/PluginTable";
import {fetchCompanyPlugins} from "../../../plugins/driver";
import RatingStarsWithText from "@/components/RatingStarsWithNumber";

const BoxWithInnerHtml = dynamic(
    () => import('@/components/BoxWithInnerHtml'),
    { ssr: false }  // This will disable server-side rendering for the component
);

export default async function CompanyDetailsPage({ params }: { params: { company_slug: string } }) {
    const company = await fetchCompanyDetails(params.company_slug);
    const plugins = await fetchCompanyPlugins(params.company_slug);
    // console.log("plugins", plugins)

    if (!company) return <NoResultsFound model_name={`Developer named "${params.company_slug}"`} />;

    return (
        <Container maxWidth="md">
            <Paper elevation={3} style={{ padding: "2em", marginTop: "2em" }}>
                <Typography variant="h4" gutterBottom>
                    {company.display_name}
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mt={2}>
                    <Typography variant="body1">
                        {company.type ? company.type : "N/A"}
                    </Typography>
                </Box>
                <List>
                    <ListItem>
                        <ListItemText
                            primary="Developer Website"
                            secondary={
                                <ExternalLink
                                    href={company.website_url || "#"}
                                >
                                    {company.website_url}
                                </ExternalLink>
                            }
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Email Exists" secondary={company.email_exists ? "Yes" : "No"} />
                        <ListItemText primary="Address Exists" secondary={company.address_exists ? "Yes" : "No"} />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Plugins Count" secondary={company.count_plugin || "N/A"} />
                        <ListItemText primary="Cumulative Downloads" secondary={formatNumberShort(company.sum_download_count)} />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Weighted Average Rating"
                            secondary={<RatingStarsWithText rating={company.weighted_avg_avg_rating} ratingCount={company.sum_rating_count}/>}
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Tags"
                            secondary={company.tags || "N/A"}
                        />
                    </ListItem>
                </List>

                {/* Blog-style Content */}

                {company.overview_summary_html ? (
                    <BoxWithInnerHtml heading="Overview Summary" htmlContent={company.overview_summary_html} />
                ) : null}
            </Paper>
            <Paper elevation={3} style={{ padding: "2em", marginTop: "2em" }}>
                <Typography variant="h4" gutterBottom>
                    Plugins of {company.display_name}
                </Typography>
                <PluginTable plugins={plugins} />
            </Paper>
        </Container>
    );
}
