// app/api/launch-agent/route.ts (if using App Router)
import { NextResponse } from "next/server";
import { MongoClient } from "mongodb";

import {MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION} from "../../../constants/consts"

const uri = MONGODB_URI as string; // Add your MongoDB URI in .env.local
const dbName = MONGODB_DB as string;
const collectionName = MONGODB_COLLECTION as string;

export async function POST(request: Request) {
  try {
    const client = new MongoClient(uri);
    await client.connect();
    const db = client.db(dbName);

    // Example: Insert a new agent
    const body = await request.json();
    const result = await db.collection(collectionName).insertOne(body);

    await client.close();

    return NextResponse.json({ success: true, result });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ success: false, error: (error as Error).message });
  }
}
