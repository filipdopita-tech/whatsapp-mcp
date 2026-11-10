package main

import (
	"context"
	"encoding/json"
	"net/http"
	"os"
	"time"

	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/types"
)

const (
	groupRequestTimeout = 30 * time.Second
	maxGroupPhotoBytes  = 5 << 20
)

// registerGroupHandlers adds group endpoints to the REST API:
//   GET  /api/groups             joined groups (JID + name), live from WhatsApp, not from the message DB
//   POST /api/group-picture      {"jid": "...@g.us"} -> current picture URL (read-only)
//   POST /api/set-group-photo    {"jid": "...@g.us", "image_path": "/abs/file.jpg"} -> new picture ID
func registerGroupHandlers(client *whatsmeow.Client) {
	http.HandleFunc("/api/groups", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), groupRequestTimeout)
		defer cancel()
		groups, err := client.GetJoinedGroups(ctx)
		if err != nil {
			http.Error(w, "GetJoinedGroups failed: "+err.Error(), http.StatusBadGateway)
			return
		}
		type groupResult struct {
			JID  string `json:"jid"`
			Name string `json:"name"`
		}
		results := make([]groupResult, 0, len(groups))
		for _, g := range groups {
			results = append(results, groupResult{JID: g.JID.String(), Name: g.Name})
		}
		writeJSON(w, results)
	})

	http.HandleFunc("/api/group-picture", func(w http.ResponseWriter, r *http.Request) {
		jid, ok := decodeGroupJID(w, r, nil)
		if !ok {
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), groupRequestTimeout)
		defer cancel()
		info, err := client.GetProfilePictureInfo(ctx, jid, &whatsmeow.GetProfilePictureParams{})
		if err != nil {
			http.Error(w, "GetProfilePictureInfo failed: "+err.Error(), http.StatusBadGateway)
			return
		}
		if info == nil {
			http.Error(w, "group has no picture", http.StatusNotFound)
			return
		}
		writeJSON(w, map[string]string{"jid": jid.String(), "url": info.URL, "id": info.ID, "type": info.Type})
	})

	http.HandleFunc("/api/set-group-photo", func(w http.ResponseWriter, r *http.Request) {
		var imagePath string
		jid, ok := decodeGroupJID(w, r, &imagePath)
		if !ok {
			return
		}
		if imagePath == "" {
			http.Error(w, "image_path is required", http.StatusBadRequest)
			return
		}
		data, err := os.ReadFile(imagePath)
		if err != nil {
			http.Error(w, "cannot read image: "+err.Error(), http.StatusBadRequest)
			return
		}
		if len(data) == 0 || len(data) > maxGroupPhotoBytes {
			http.Error(w, "image must be a non-empty JPEG up to 5 MB", http.StatusBadRequest)
			return
		}
		if http.DetectContentType(data) != "image/jpeg" {
			http.Error(w, "image must be JPEG", http.StatusBadRequest)
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), groupRequestTimeout)
		defer cancel()
		pictureID, err := client.SetGroupPhoto(ctx, jid, data)
		if err != nil {
			http.Error(w, "SetGroupPhoto failed: "+err.Error(), http.StatusBadGateway)
			return
		}
		writeJSON(w, map[string]string{"jid": jid.String(), "picture_id": pictureID})
	})
}

// decodeGroupJID reads {"jid": ..., "image_path": ...} from a POST body and validates the group JID.
func decodeGroupJID(w http.ResponseWriter, r *http.Request, imagePath *string) (types.JID, bool) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return types.JID{}, false
	}
	var req struct {
		JID       string `json:"jid"`
		ImagePath string `json:"image_path"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request format", http.StatusBadRequest)
		return types.JID{}, false
	}
	jid, err := types.ParseJID(req.JID)
	if err != nil || jid.Server != types.GroupServer {
		http.Error(w, "jid must be a group JID (...@g.us)", http.StatusBadRequest)
		return types.JID{}, false
	}
	if imagePath != nil {
		*imagePath = req.ImagePath
	}
	return jid, true
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(v); err != nil {
		http.Error(w, "encode failed: "+err.Error(), http.StatusInternalServerError)
	}
}
