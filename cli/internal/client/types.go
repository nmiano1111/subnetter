package client

import (
	"encoding/json"
	"strings"
	"time"
)

type APITime struct {
	time.Time
}

func (t *APITime) UnmarshalJSON(b []byte) error {
	s := strings.Trim(string(b), `"`)
	if s == "" {
		return nil
	}

	// Try full RFC3339
	if tt, err := time.Parse(time.RFC3339Nano, s); err == nil {
		t.Time = tt
		return nil
	}

	// Fallback: naive timestamp → treat as UTC
	layouts := []string{
		"2006-01-02T15:04:05.999999", // microseconds, no TZ
		"2006-01-02T15:04:05",        // seconds, no TZ
	}
	for _, l := range layouts {
		if tt, err := time.ParseInLocation(l, s, time.UTC); err == nil {
			t.Time = tt
			return nil
		}
	}

	return json.Unmarshal(b, &t.Time) // last resort
}

type TenantOut struct {
	ID        string  `json:"id"`
	Name      string  `json:"name"`
	CreatedAt APITime `json:"created_at"`
}

type VrfOut struct {
	ID        string  `json:"id"`
	TenantID  string  `json:"tenant_id"`
	Name      string  `json:"name"`
	RD        *string `json:"rd"`
	CreatedAt APITime `json:"created_at"`
}

type PrefixOut struct {
	ID        string  `json:"id"`
	VRFID     string  `json:"vrf_id"`
	CIDR      string  `json:"cidr"`
	Status    string  `json:"status"`
	Desc      string  `json:"description"`
	ParentID  *string `json:"parent_id"`
	CreatedAt APITime `json:"created_at"`
}

type NextIPOut struct {
	ID      string `json:"id"`
	Address string `json:"address"`
}

type APIError struct {
	Err     string                 `json:"error"`
	Message string                 `json:"message"`
	Details map[string]interface{} `json:"details"`
}

func (e *APIError) Error() string {
	if e == nil {
		return "<nil>"
	}
	if e.Message != "" {
		return e.Message
	}
	return e.Err
}
