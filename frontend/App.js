import React, { useState, useEffect } from 'react';
import { View, Text, Button, TextInput, Image, FlatList } from 'react-native';
import { createClient } from '@supabase/supabase-js';
import * as Location from 'expo-location';

const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export default function App() {
  const [email, setEmail] = useState('');
  const [user, setUser] = useState(null);
  const [description, setDescription] = useState('');
  const [issues, setIssues] = useState([]);

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.warn('Location permission not granted');
      }
    })();
  }, []);

  async function signIn() {
    const { data, error } = await supabase.auth.signInWithOtp({ email });
    if (error) return alert(error.message);
    alert('Check your email for login link');
  }

  async function submitIssue() {
    const loc = await Location.getCurrentPositionAsync({});
    const fd = new FormData();
    fd.append('title', description.slice(0, 30) || 'Issue');
    fd.append('description', description);
    fd.append('lat', String(loc.coords.latitude));
    fd.append('lng', String(loc.coords.longitude));

    // Attach images if any (example: from an image picker stored in state 'photos')
    // photos should be an array of { uri, name, type }
    if (photos && photos.length) {
      photos.forEach((p, idx) => {
        fd.append('images', {
          uri: p.uri,
          name: p.name || `photo-${idx}.jpg`,
          type: p.type || 'image/jpeg'
        });
      });
    }

    const headers = {};
    if (user && user.access_token) {
      headers['Authorization'] = `Bearer ${user.access_token}`;
    }

    const res = await fetch('http://localhost:4000/issues', {
      method: 'POST',
      headers,
      body: fd
    });
    await res.json();
    alert('Submitted');
    fetchIssues();
  }

  async function fetchIssues() {
    // Simple list fetch via Supabase
    const { data, error } = await supabase.from('issues').select('*').order('created_at', { ascending: false }).limit(20);
    if (!error) setIssues(data || []);
  }

  return (
    <View style={{ padding: 16, paddingTop: 60 }}>
      {!user ? (
        <>
          <Text>Email</Text>
          <TextInput value={email} onChangeText={setEmail} style={{ borderWidth: 1, marginBottom: 8 }} />
          <Button title="Sign in / Sign up" onPress={signIn} />
        </>
      ) : (
        <Text>Welcome {user.email}</Text>
      )}

      <Text style={{ marginTop: 24 }}>Report an issue</Text>
      <TextInput value={description} onChangeText={setDescription} style={{ borderWidth: 1, height: 80, marginBottom: 8 }} multiline />
      <Button title="Submit Issue" onPress={submitIssue} />

      <Button title="Refresh Issues" onPress={fetchIssues} />
      <FlatList data={issues} keyExtractor={i => i.id} renderItem={({ item }) => (
        <View style={{ padding: 8, borderBottomWidth: 1 }}>
          <Text>{item.title}</Text>
          <Text>{item.description}</Text>
          <Text>{item.status}</Text>
        </View>
      )} />
    </View>
  );
}
