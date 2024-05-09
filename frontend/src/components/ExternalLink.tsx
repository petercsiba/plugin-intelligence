import Link from 'next/link';
import { OpenInNew } from '@mui/icons-material';
import { Typography, IconButton } from '@mui/material';
import { ReactNode } from 'react';

interface ExternalLinkProps {
  href: string;
  children: ReactNode;
}

const ExternalLink = ({ href, children, ...props }: ExternalLinkProps) => {
  return (
    <Typography component="span">
      <Link href={href} target="_blank" rel="noopener noreferrer" {...props}>
        {children}
        <IconButton aria-label="Open in new window" size="small">
          <OpenInNew fontSize="small" />
        </IconButton>
      </Link>
    </Typography>
  );
};

export default ExternalLink;
