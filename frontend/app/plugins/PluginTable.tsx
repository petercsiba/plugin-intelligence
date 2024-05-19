// PluginTable.tsx
import Image from 'next/image';
import React, { useState } from 'react';
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Box } from '@mui/material';
import NextLink from 'next/link';
import ListBoxOneLine from "@/components/ListBoxOneLine";
import {formatCurrency, formatNumberShort} from "@/utils";
import {TopPluginResponse} from "./models";

interface PluginTableProps {
  plugins: TopPluginResponse[];
}

const PluginTable: React.FC<PluginTableProps> = ({ plugins }) => {
    const [visibleRows, setVisibleRows] = useState(6);

    const handleLoadMore = () => {
        setVisibleRows(plugins.length);
    };

  return (

      <TableContainer component={Paper}>
        <Table size="small"> {/* Smaller cell padding */}
          <TableHead>
            <TableRow>
              <TableCell>Logo</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Main Tags</TableCell>
              <TableCell>Revenue Estimate</TableCell>
              <TableCell>Downloads</TableCell>
              <TableCell>Lowest Paid Tier</TableCell>
              <TableCell>Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {plugins.slice(0, visibleRows).map((plugin) => (
                <TableRow key={plugin.id}>
                  <TableCell>
                    {plugin.img_logo_link ? (
                        <Image
                            src={plugin.img_logo_link}
                            alt={plugin.name}
                            width={48}
                            height={48}
                        />
                    ) : (
                        ''
                    )}
                  </TableCell>
                  <TableCell style={{ fontWeight: 'bold' }}>
                      {plugin.name}
                  </TableCell>
                  <TableCell>
                    <ListBoxOneLine listOfStrings={plugin.main_tags} />
                  </TableCell>
                  <TableCell>
                    {plugin.revenue_lower_bound && plugin.revenue_upper_bound ? (
                        `${formatCurrency(plugin.revenue_lower_bound)} - ${formatCurrency(plugin.revenue_upper_bound)}`
                    ) : 'N/A'}
                  </TableCell>
                  <TableCell>{formatNumberShort(plugin.user_count)}</TableCell>
                  <TableCell>{formatCurrency(plugin.lowest_paid_tier)}</TableCell>
                  <TableCell>
                    <NextLink href={`/plugins/${plugin.id}/detail`} passHref>
                      <Button color="primary" fullWidth>
                        {/* Full width on mobile */}
                        Details
                      </Button>
                    </NextLink>
                  </TableCell>
                </TableRow>
            ))}
          </TableBody>
        </Table>

        {visibleRows < plugins.length && (
            <Box display="flex" justifyContent="center" width="100%" my={2}>
                <Button variant="contained" color="primary" onClick={handleLoadMore}>
                    Load More
                </Button>
            </Box>
        )}
      </TableContainer>
  );
};

export default PluginTable;
