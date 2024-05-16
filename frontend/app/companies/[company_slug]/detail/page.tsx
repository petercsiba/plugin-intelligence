import React from "react";
import {
    Container,
    Paper,
    Typography,
    List,
    ListItem,
    ListItemText,
    Rating,
} from "@mui/material";
import Box from "@mui/material/Box";
import ExternalLink from "@/components/ExternalLink";
import dynamic from "next/dynamic";
import {fetchCompanyDetails} from "../../driver";
import NoResultsFound from "@/components/NoResultsFound";
import {formatNumber, formatNumberShort } from "@/utils";

const BoxWithInnerHtml = dynamic(
    () => import('@/components/BoxWithInnerHtml'),
    { ssr: false }  // This will disable server-side rendering for the component
);

export default async function CompanyDetailsPage({ params }: { params: { company_slug: string } }) {
    const company = await fetchCompanyDetails(params.company_slug);

    if (!company) return <NoResultsFound model_name={`Company named "${params.company_slug}"`} />;

    return (
        <Container maxWidth="md">
            <Paper elevation={3} style={{ padding: "2em", marginTop: "2em" }}>
                <Typography variant="h4" gutterBottom>
                    {company.display_name} ({company.legal_name})
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mt={2}>
                    <Typography variant="body1">
                        {company.type ? company.type : "N/A"}
                    </Typography>
                </Box>
                <List>
                    <ListItem>
                        <ListItemText
                            primary="Website"
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
                        <ListItemText primary="Total Downloads" secondary={formatNumberShort(company.sum_download_count)} />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Weighted Average Rating" secondary={
                            <Rating
                                name="company-weighted-avg-rating"
                                value={company.weighted_avg_avg_rating ? company.weighted_avg_avg_rating : 0}
                                precision={0.25}
                                readOnly
                            />
                        } />
                        <ListItemText primary="Total Ratings" secondary={formatNumberShort(company.sum_rating_count)} />
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
        </Container>
    );
}
