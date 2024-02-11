"use client";
import React from "react";
import {
  AppShell,
  Burger,
  Container,
  Divider,
  Group,
  ScrollArea,
  Space,
  Center,
  Loader,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { EmissionsEntry } from "./_components/EmissionsEntry";
import { Header } from "./_components/Header";
import { API_BASE } from "./helpers";

export default function HomePage() {
  // Make API call to get people
  const [people, setPeople] = React.useState([]);
  const [max_emissions, setMaxEmissions] = React.useState(0);
  React.useEffect(() => {
    fetch(API_BASE + "/get_people")
      .then((response) => response.json())
      .then((data) => {
        setPeople(data);
        console.log(data);
        let max_emissions = 0;
        for (let person of data) {
          if (person["total_emissions_kg"] > max_emissions) {
            max_emissions = person["total_emissions_kg"];
          }
        }
        setMaxEmissions(max_emissions);
      });
  }, []);

  return (
    <>
      <Header
        links={[
          { label: "Home", link: "/" },
          { label: "About", link: "/about" },
        ]}
      />
      <Container size="lg" style={{ paddingTop: 50 }}>
        <ScrollArea pb={50}>
          {people && people.length > 0 && (
            <Group gap={20} wrap="nowrap">
              {people.map((person: any, index: number) => {
                let total = 0
                person.flights.map((flight: any) => {
                  total += flight.emissions_kg
                })
                return (
                  <>
                    <EmissionsEntry
                      key={index}
                      entry={person}
                      max_emissions={max_emissions}
                    />
                    {
                      index !== people.length - 1 &&
                      <Divider orientation="vertical" />
                    }
                  </>
                );
              })}
              {people.map((person: any, index: number) => {
                let total = 0
                person.flights.map((flight: any) => {
                  total += flight.emissions_kg
                })
                return (
                  <>
                    <EmissionsEntry
                      key={index}
                      entry={person}
                      max_emissions={max_emissions}
                    />
                    {
                      index !== people.length - 1 &&
                      <Divider orientation="vertical" />
                    }
                  </>
                );
              })}
              {people.map((person: any, index: number) => {
                let total = 0
                person.flights.map((flight: any) => {
                  total += flight.emissions_kg
                })
                return (
                  <>
                    <EmissionsEntry
                      key={index}
                      entry={person}
                      max_emissions={max_emissions}
                    />
                    {
                      index !== people.length - 1 &&
                      <Divider orientation="vertical" />
                    }
                  </>
                );
              })}
            </Group>
          )}
          {!people ||
            (people.length === 0 && (
              <Center>
                <Space h="40vh" />
                <Loader />
              </Center>
            ))}
        </ScrollArea>
      </Container>
      <Space h={100} />
    </>
  );
}
