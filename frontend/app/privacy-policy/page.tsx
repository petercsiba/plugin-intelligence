import React from 'react';
import {
    Container,
    Typography,
    Link,
    List,
    ListItem,
    ListItemText,
} from '@mui/material';

const PrivacyPolicyPage: React.FC = () => {
    return (
        <Container maxWidth="md" sx={{ padding: '2rem 0' }}>
            <Typography variant="h3" gutterBottom>Privacy Policy</Typography>
            <Typography variant="body1" gutterBottom><i>Last Updated May 22, 2024</i></Typography>

            <Typography variant="body1" paragraph>
                At Plugin Intelligence, we prioritize data privacy and handle it with utmost seriousness.
                Our customers trust us to empower their businesses with clean, compliant,
                and ethically sourced data while maintaining the highest standards of privacy.
                Our products and services operate in a global context,
                and we continuously monitor the dynamic global privacy landscape
                to ensure complete compliance with privacy laws,
                including the European Union's GDPR and California's CCPA.
            </Typography>
            <Typography variant="body1" paragraph>
                This Privacy Policy addresses both users who actively choose to use our
                services and individuals whose personal data we may process as part of our operation.
            </Typography>
            <Typography variant="body1" paragraph>
                Please read on for a detailed breakdown of our privacy policy,
                or contact us with any questions regarding our policy or data legislation compliance.
            </Typography>
            <Typography variant="body1" paragraph>
                Plugin Intelligence ("<b>Plugin-Intelligence</b>", "<b>we</b>", or "<b>us</b>")
                is the owner of the website plugin-intelligence.com ("<b>the Site</b>")
                and any accompanying services, features, content, and applications offered by us
                (collectively referred herein as "<b>the Services</b>").
                We are concerned about your privacy and have designed this Privacy Policy
                to help you decide whether to use the Services and to provide
                all required information about our privacy practices.
                If applicable to you, by accessing and using the Services or providing information
                to us in other formats, you agree and accept the terms of this Privacy Policy
                as amended from time to time and consent to the collection and use of information
                in the manner set out in this Privacy Policy.
                We encourage you to review this Privacy Policy carefully and periodically refer
                to it so that you understand it and any subsequent changes made to it.
                IF YOU DO NOT AGREE TO THE TERMS OF THIS PRIVACY POLICY,
                PLEASE STOP USING THE SERVICES IMMEDIATELY.
            </Typography>

            <Typography variant="h4" id="info-types" gutterBottom>What types of information do we collect?</Typography>
            <Typography variant="body1" paragraph>
                We collect the following types of data from you when you use the Services ("<b>User Data</b>"):
            </Typography>
            <List>
                <ListItem>
                    <ListItemText primary="Non-Personal Information" secondary="This is information that is un-identified and non-identifiable, which is generated by a user's activity. Such non-personal information may include the following information: browser type, web pages you visit, time spent on those pages, access times and dates." />
                </ListItem>
                <ListItem>
                    <ListItemText primary="Personal Information" secondary="Personal information is information that identifies you or may identify you. The Personal Information we collect and retain includes your IP address, your name and email address, identifying documents (driver license/ID/passport), office/home address, screen name, payment and billing information, or other information we may ask from time to time as required for the on-boarding process and services provisioning." />
                </ListItem>
            </List>
            <Typography variant="body1" paragraph>
                We may also collect publicly posted personal data from various online sources. Such information will include, in most cases, basic contact information, such as name, email, and job title ("<b>Public Data</b>").
            </Typography>

            <Typography variant="h4" id="info-processing" gutterBottom>Legal basis for processing</Typography>
            <Typography variant="body1" paragraph>
                Processing of User Data is necessary for the performance of our contractual obligations towards you and providing you with our services, to protect our legitimate interests, and to comply with our legal obligations.
            </Typography>
            <Typography variant="body1" paragraph>
                Processing of Public Data is done in accordance with our legitimate interest, as long as such interest does not override your fundamental rights and freedom.
            </Typography>

            <Typography variant="h4" id="info-use" gutterBottom>How do we use your information?</Typography>
            <Typography variant="body1" paragraph>
                We use User Data to provide you with the Service and to comply with our legal requirements and internal guidelines. This means that we will use the information to set up your account, provide you with support regarding the Service, communicate with you for updates, marketing offers, or concerns you may have, and conduct statistical and analytical research to improve the Service. We may use Public Data to provide our users with our Services.
            </Typography>

            <Typography variant="h4" id="info-share" gutterBottom>Information we share</Typography>
            <Typography variant="body1" paragraph>
                We do not rent or sell any User Data. We may share Public Data with our users to provide our Services.
            </Typography>
            <Typography variant="body1" paragraph>
                We may disclose Personal Information to other trusted third-party service providers or partners for providing you with the Services, storage, and analytics, and to comply with our legal requirements and internal guidelines. We may also transfer or disclose Personal Information to our subsidiaries and affiliated companies.
            </Typography>
            <Typography variant="body1" paragraph>
                We may also share your Personal Information and other information in special cases if we have good
                reason to believe that it is necessary to:
                <ul style={{ listStyleType: 'none'}}>
                    <li> (1) comply with law, regulation, subpoena, or court order;</li>
                    <li> (2) detect, prevent or otherwise address fraud, security, violation of our policies, or technical
                        issues;
                    </li>
                    <li>(3) enforce the provisions of this Privacy Policy or any other agreements between you and us, including
                        investigation of potential violations thereof; </li>
                    <li>(4) protect against harm to the rights, property, or safety of us, our partners, our affiliates, users,
                        or the public.</li>
                </ul>
            </Typography>

            <Typography variant="h4" id="data-outside-eea" gutterBottom>Processing of data outside the EEA</Typography>
            <Typography variant="body1" paragraph>
                Note that we are based in California, USA, and some of the data recipients listed above may be located outside the European Economic Area (EEA). In such cases, we will share your data only with recipients located in such countries as approved by the European Commission as providing an adequate level of data protection or enter into legal agreements ensuring an adequate level of data protection.
            </Typography>

            <Typography variant="h4" id="security" gutterBottom>Security and Confidentiality</Typography>
            <Typography variant="body1" paragraph>
                We use industry-standard information, security tools, and measures, as well as internal procedures and strict guidelines to prevent information misuse and data leakage. Our employees are subject to confidentiality obligations. We use measures and procedures that substantially reduce the risks of data misuse, but we cannot guarantee that our systems will be absolutely safe. If you become aware of any potential data breach or security vulnerability, you are requested to contact us immediately. We will use all measures to investigate the incident, including preventive measures, as required.
            </Typography>

            <Typography variant="h4" id="rights" gutterBottom>Your Choices and Rights</Typography>
            <Typography variant="body1" paragraph>
                We strive to give you ways to update your information quickly or to delete it - unless we have to keep that information for legitimate business or legal purposes. When updating your personal information, we may ask you to verify your identity before we can act on your request.
            </Typography>
            <Typography variant="body1" paragraph>
                If you are a resident of the European Union, note that the following rights specifically apply regarding your personal information:
                <ul style={{ listStyleType: 'none'}}>
                    <li>(1) Receive confirmation as to whether or not personal information concerning you is being processed, and access your stored personal information, together with supplementary information;</li>
                    <li>(2) Receive a copy of personal information you directly volunteer to us in a structured, commonly used, and machine-readable format;</li>
                    <li>(3) Request rectification of your personal information that is in our control;</li>
                    <li>(4) Request erasure of your personal information;</li>
                    <li>(5) Object to the processing of personal information by us;</li>
                    <li>(6) Request to restrict processing of your personal information by us;</li>
                    <li>(7) Lodge a complaint with a supervisory authority.</li>
                </ul>
            </Typography>
            <Typography variant="body1" paragraph>
                However, note that these rights are not absolute, and may be subject to our own legitimate interests and regulatory requirements.
            </Typography>
            <Typography variant="body1" paragraph>
                To exercise such rights, you may contact us at: <Link href="mailto:gdpr@plugin-intelligence.com">gdpr@plugin-intelligence.com</Link>
            </Typography>

            <Typography variant="h4" id="retention" gutterBottom>Retention</Typography>
            <Typography variant="body1" paragraph>
                We will retain your personal information for as long as necessary to provide the Service, and as necessary to comply with our legal obligations, resolve disputes, and enforce our policies. Retention periods shall be determined taking into account the type of information collected and the purpose for which it is collected, bearing in mind the requirements applicable to the situation and the need to destroy outdated, unused information at the earliest reasonable time. Under applicable regulations, we will keep records containing client personal data, account opening documents, communications, and anything else as required by applicable laws and regulations.
            </Typography>

            <Typography variant="h4" id="corporate-transaction" gutterBottom>Corporate Transaction</Typography>
            <Typography variant="body1" paragraph>
                We may share information, including personal information, in the event of a corporate transaction (e.g., sale of substantial assets, merger, consolidation, or asset sale) of the Company. In such an event, the acquiring company or transferee will assume the rights and obligations described in this Privacy Policy.
            </Typography>
            <Typography variant="body1" paragraph>
                If we are involved in a bankruptcy, insolvency, or receivership, we may have no control over the use and transfer of your personal information.
            </Typography>

            <Typography variant="h4" id="privacy-change" gutterBottom>Changes to this Privacy Policy</Typography>
            <Typography variant="body1" paragraph>
                This Policy may be revised from time to time at our sole discretion, so check it regularly. The last revision will be reflected in the "Last Updated" heading. Any change to this policy will be posted on the Site. Your continued use of the Services following any such changes will be considered as your consent to the amended Privacy Policy.
            </Typography>

            <Typography variant="h4" id="contact-us" gutterBottom>Contact Us</Typography>
            <Typography variant="body1" paragraph>
                If you feel that your privacy was not treated in accordance with our Privacy Policy, or if you believe that your privacy has been compromised by any person in the course of using the Services, contact Plugin-Intelligence at: <Link href="mailto:privacy@plugin-intelligence.com">privacy@plugin-intelligence.com</Link> and our Privacy Officer shall promptly investigate.
            </Typography>
        </Container>
    );
};

export default PrivacyPolicyPage;