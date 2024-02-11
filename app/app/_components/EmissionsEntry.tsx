"use client";
import React, { useState } from "react";
import { HoverCard, Center, Image, Text, Space } from "@mantine/core";
import { EmissionsCard } from "./EmissionsCard";
import { STATIC_BASE, kgFormat } from "../helpers";
import "./EmissionsEntry.scss";

const colors = ["#f1ca5f", "#f4ae53", "#f49250", "#ee7653", "#e45a5a"];

export function EmissionsEntry(props: { entry: any; max_emissions: number }) {
  const total_height = props.entry["total_emissions_kg"] / props.max_emissions;
  const bar_elements = props.entry["flights"].map(
    (flight: any, index: number) => {
      const height =
        (flight["emissions_kg"] / props.entry["total_emissions_kg"]) *
        total_height *
        100;
      const color =
        colors[
          Math.max(Math.min(Math.floor(height / 1.4), colors.length - 1), 0)
        ];
      return (
        <HoverCard key={index} closeDelay={0} withArrow position="right">
          <HoverCard.Target>
            <div
              className="bar-segment"
              style={{
                height: height + "%",
                backgroundColor: color,
                width: "100%",
              }}
            ></div>
          </HoverCard.Target>
          <HoverCard.Dropdown>
            <EmissionsCard entry={flight} />
          </HoverCard.Dropdown>
        </HoverCard>
      );
    }
  );

  return (
    <div className="emissions-entry">
      <div className="bar-container">{bar_elements}</div>
      <div className="ee-info">
        <Image
          src={STATIC_BASE + props.entry["image"]}
          alt={"Profile picture of " + props.entry["name"]}
          radius="50%"
          w={60}
          h={60}
          mb={8}
          mt={20}
          style={{ border: "3px solid #fd7e14" }}
        />
        <Text c="gray.7" size="xs" truncate fw="bold">
          {props.entry["name"]}
        </Text>
        <Space h={20} />

        <Text c="orange.6" size="md" fw="bold" ff="IBM Plex Mono" truncate>
          {kgFormat(props.entry["total_emissions_kg"])}
        </Text>
        <Text c="gray.7" size="xs">
          CO<sub>2</sub> eq
        </Text>
        {/* <Space h={20} /> */}

        {/* <Text c="orange.6" size="m" fw="bold">
          {props.entry["total_flight_count"]}
        </Text>
        <Text c="gray.7" size="xs">
          flights
        </Text>
        <Space h={20} />

        <Text c="orange.6" size="m" fw="bold">
          {props.entry["total_flight_distance_km"].toFixed(0)}
        </Text>
        <Text c="gray.7" size="xs">
          km
        </Text> */}
      </div>
    </div>
  );
}
