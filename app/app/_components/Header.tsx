"use client";
import React, { useState } from "react";
import { Container, Group, Burger, Button, ButtonGroup, Text } from "@mantine/core";
import styles from "./Header.module.scss";

const links = [
  { label: "Home", link: "/" },
  { label: "About", link: "/about" },
];

export function Header(props: { links: { label: string; link: string }[] }) {
  // const activeLink = props.links.find((link) => link.link === window.location.pathname)?.link;

  const items = links.map((link) => (
    <a key={link.link} href={link.link} className={styles.menuItem}>
      {link.label}
    </a>
  ));

  return (
    <header>
      <Container size="lg">
        <Group wrap="nowrap" justify="space-between"  pt={20}>
          <Text fw={900} ff="IBM Plex Mono" fz={22} c="gray.8">emissions.win</Text>
          <Group gap={20}>{items}</Group>
        </Group>
      </Container>
    </header>
  );
}
