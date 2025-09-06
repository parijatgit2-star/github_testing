import React, { useState, useEffect } from 'react';
import { View, Text, Button, TextInput, Image, FlatList, Alert } from 'react-native';
import { createClient } from '@supabase/supabase-js';
import * as Location from 'expo-location';
import * as ImagePicker from 'expo-image-picker';

const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;


let _supabase = null;
/**
 * Returns a singleton instance of the Supabase client.
 * Initializes the client if it hasn't been created yet.
 * @returns {import('@supabase/supabase-js').SupabaseClient|null} The Supabase client instance, or null if configuration is missing.
 */
function getSupabase() {
  if (_supabase) return _supabase;
  if (!SUPABASE_URL || !SUPABASE_KEY) return null;
  try {
    _supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
    return _supabase;
  } catch (e) {
    return null;
  }
}

/**
 * The main component for the mobile application.
 *
 * This component handles user authentication, issue submission with image uploads,
 * and viewing a list of existing issues. It manages all the necessary state
 * and side effects for the application's core functionality.
 * @returns {React.ReactElement} The main application component.
 */
export default function App() {
  const [email, setEmail] = useState('');
  const [user, setUser] = useState(null);
  const [photos, setPhotos] = useState([]);
  const [description, setDescription] = useState('');
  const [issues, setIssues] = useState([]);

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.warn('Location permission not granted');
      }
    })();
    // populate current session/user if available
    (async () => {
      try {
        const sb = getSupabase();
        if (!sb) return;
        const { data } = await sb.auth.getSession();
        const session = data?.session || null;
        if (session) {
          setUser({
            access_token: session.access_token,
            user: session.user,
            email: session.user?.email,
          });
        }
      } catch (e) {
        // ignore
      }
    })();

    // listen for auth state changes and keep user updated
  const sb = getSupabase();
  const { data: listener } = sb ? sb.auth.onAuthStateChange((event, session) => {
      try {
        const s = session?.session || session || null;
        if (s) {
          setUser({ access_token: s.access_token, user: s.user, email: s.user?.email });
        } else {
          setUser(null);
        }
      } catch (e) {
        // ignore
      }
  }) : { data: null };
    return () => {
      try {
        listener?.subscription?.unsubscribe?.();
      } catch (e) {}
    };
  }, []);

  /**
   * Initiates the Supabase "magic link" sign-in process.
   * Sends a one-time password (OTP) link to the user's email.
   */
  async function signIn() {
    const sb = getSupabase();
    if (!sb) return Alert.alert('Missing configuration', 'Supabase is not configured in this environment.');
    const { data, error } = await sb.auth.signInWithOtp({ email });
    if (error) return alert(error.message);
    alert('Check your email for login link');
  }

  /**
   * Submits a new issue to the backend API.
   * Gathers the current location, description, and any selected photos,
   * then sends them as a multipart/form-data request.
   */
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
    const result = await res.json().catch(() => null);
    if (!res.ok) {
      console.warn('submitIssue failed', res.status, result);
      Alert.alert('Submit failed', JSON.stringify(result || {}));
    } else {
      Alert.alert('Submitted');
      fetchIssues();
    }
  }

  /**
   * Fetches the latest issues from the Supabase database.
   */
  async function fetchIssues() {
    // Simple list fetch via Supabase
    try {
      const sb = getSupabase();
      if (!sb) return;
      const { data, error } = await sb.from('issues').select('*').order('created_at', { ascending: false }).limit(20);
      if (!error) setIssues(data || []);
    } catch (e) {
      console.warn('fetchIssues error', e);
    }
  }

  useEffect(() => {
    // fetch initial issues on mount
    fetchIssues();
  }, []);

  /**
   * Opens the device's image library to allow the user to select photos.
   * Uses `expo-image-picker` to handle the selection process.
   */
  async function pickImage() {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission required', 'Permission to access photos is required to attach images.');
        return;
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.7,
        allowsEditing: true,
      });
      if (!result.cancelled) {
        // result.uri, result.type differ across SDKs; standardize into an object usable in RN FormData
        const file = {
          uri: result.uri,
          name: result.uri.split('/').pop(),
          type: 'image/jpeg',
        };
        setPhotos(prev => [...prev, file]);
      }
    } catch (e) {
      console.warn('pickImage error', e);
    }
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
      <View style={{ flexDirection: 'row', gap: 8, marginBottom: 8 }}>
        <Button title="Pick Photo" onPress={pickImage} />
        <Button title="Submit Issue" onPress={submitIssue} />
      </View>

      <FlatList
        data={photos}
        horizontal
        keyExtractor={(p, i) => `${p.uri}-${i}`}
        renderItem={({ item }) => (
          <Image source={{ uri: item.uri }} style={{ width: 80, height: 80, marginRight: 8 }} />
        )}
      />

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
