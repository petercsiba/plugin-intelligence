import React from "react";
import NextLink from "next/link";
import {
    Button,
    Container,
    Paper,
    Rating,
    Typography,
    List,
    ListItem,
    ListItemText,
} from "@mui/material";
import Box from "@mui/material/Box";
import {PluginDetailsResponse} from "../models";
import ExternalLink from "@/components/ExternalLink";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

// Function to fetch plugin details
async function fetchPluginDetails(plugin_id: string): Promise<PluginDetailsResponse | null> {
    const response = await fetch(`${baseUrl}/plugin/${plugin_id}/details`, {
        cache: "no-store", // Adjust caching as needed
    });

    if (!response.ok) {
        console.error(`Error fetching plugin details: ${response.statusText}`);
        return null;
    }

    return await response.json();
}

export default async function PluginDetailsPage({ params }: { params: { plugin_id: string } }) {
    const plugin = await fetchPluginDetails(params.plugin_id);
    if (!plugin) {
        return (
            <div>
                <p>Oops! Something went wrong. Please try again later or go back to the main page.</p>
                <NextLink href="/">
                    <Button variant="contained" color="primary">
                        Back to Main Page
                    </Button>
                </NextLink>
            </div>
        );
    }

    // Format ranges
    const revenueRange = plugin && plugin.lower_bound && plugin.upper_bound
        ? `\$${plugin.lower_bound} - \$${plugin.upper_bound}`
        : "N/A";

    // Convert comma-separated lists
    const mainIntegrations = plugin && plugin.main_integrations ? plugin.main_integrations.split(",").join(", ") : "N/A";
    const searchTerms = plugin && plugin.search_terms ? plugin.search_terms.split(",").join(", ") : "N/A";
    const tags = plugin && plugin.tags ? plugin.tags.split(",").join(", ") : "N/A";

    return (
        <Container maxWidth="md">
            <Paper elevation={3} style={{ padding: "2em", marginTop: "2em" }}>
                <Typography variant="h4" gutterBottom>
                    {plugin.name} ({plugin.plugin_type})
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mt={2}>
                    <Typography variant="body1">
                        {plugin.user_count ? `${plugin.user_count.toLocaleString()} Users` : "N/A"}
                    </Typography>
                    <Rating
                        name="plugin-rating"
                        value={plugin.rating ? parseFloat(plugin.rating) : 0}
                        precision={0.5}
                        readOnly
                    />
                    <Typography variant="body2">
                        {plugin.rating_count ? `${plugin.rating_count.toLocaleString()} Ratings` : "N/A"}
                    </Typography>
                </Box>
                <List>
                    <ListItem>
                        <ListItemText
                            primary="Marketplace ID"
                            secondary={plugin.google_id || "N/A"}
                        />
                        <ListItemText
                            primary={`See on ${plugin.plugin_type} Marketplace`}
                            secondary={
                                <ExternalLink
                                    href={plugin.link || "#"}
                                >
                                    Link
                                </ExternalLink>
                            }
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Revenue Estimate" secondary={revenueRange} />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Main Integrations" secondary={mainIntegrations} />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Search Terms" secondary={searchTerms} />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Tags" secondary={tags} />
                    </ListItem>
                </List>

                {/* Blog-style Content */}

                {plugin.elevator_pitch ? (
                    <Box mt={4}>
                        <Typography variant="h5">Elevator Pitch</Typography>
                        <Typography paragraph>{plugin.elevator_pitch || "N/A"}</Typography>
                    </Box>
                ) : null}
                <Box mt={4}>
                    <Typography variant="h5">Overview Summary</Typography>
                    <Typography paragraph>{plugin.overview_summary || "N/A"}</Typography>
                </Box>
                {plugin.full_text_analysis_html ? (
                    <Box mt={4}>
                        <Typography variant="h5">Full Text Analysis</Typography>
                        <Typography paragraph dangerouslySetInnerHTML={{__html: plugin.full_text_analysis_html}}>
                        </Typography>
                    </Box>
                ):null}
            </Paper>
        </Container>
    );
}
