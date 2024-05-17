// PluginTable.tsx
import Image from 'next/image';
import React from 'react';
import { Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button } from '@mui/material';
import NextLink from 'next/link';
import ListBoxOneLine from "@/components/ListBoxOneLine";
import {formatCurrency, formatNumberShort} from "@/utils";
import {TopPluginResponse} from "./models";

interface PluginTableProps {
  plugins: TopPluginResponse[];
}

const PluginTable: React.FC<PluginTableProps> = ({ plugins }) => {
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
            {plugins.map((plugin) => (
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
                  <TableCell style={{ fontWeight: 'bold' }}>{plugin.name}</TableCell>
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
                      <Button variant="contained" color="primary" fullWidth>
                        {/* Full width on mobile */}
                        View
                      </Button>
                    </NextLink>
                  </TableCell>
                </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
  );
};

export default PluginTable;
